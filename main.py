from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

from rabe_demo.benchmark import BenchmarkRunner
from rabe_demo.scheme import OfflineToken, RevocableAccessSystem, read_json, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IIoT revocable attribute-based access-control prototype")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize system state")
    p_init.add_argument("--state", default="state/system.json")

    p_add = sub.add_parser("add-user", help="Register a user and issue keys")
    p_add.add_argument("--state", default="state/system.json")
    p_add.add_argument("--user", required=True)
    p_add.add_argument("--attrs", nargs="+", required=True)

    p_encrypt = sub.add_parser("encrypt", help="Encrypt a file under a policy")
    p_encrypt.add_argument("--state", default="state/system.json")
    p_encrypt.add_argument("--owner", required=True)
    p_encrypt.add_argument("--dataset", required=True)
    p_encrypt.add_argument("--policy", required=True)
    p_encrypt.add_argument("--input", required=True)
    p_encrypt.add_argument("--output", required=True)

    p_decrypt = sub.add_parser("decrypt", help="Request outsourced decrypt and finalize locally")
    p_decrypt.add_argument("--state", default="state/system.json")
    p_decrypt.add_argument("--user", required=True)
    p_decrypt.add_argument("--cipher", required=True)
    p_decrypt.add_argument("--output")

    p_revoke = sub.add_parser("revoke-user", help="Revoke user and rotate the target dataset")
    p_revoke.add_argument("--state", default="state/system.json")
    p_revoke.add_argument("--user", required=True)
    p_revoke.add_argument("--dataset", required=True)

    p_rewrap = sub.add_parser("rewrap", help="Rewrap ciphertext after dataset rotation")
    p_rewrap.add_argument("--state", default="state/system.json")
    p_rewrap.add_argument("--cipher", required=True)
    p_rewrap.add_argument("--output")

    p_demo = sub.add_parser("demo", help="Run an end-to-end demonstration")
    p_demo.add_argument("--state", default="demo_state/system.json")

    p_bench = sub.add_parser("benchmark", help="Run automated experiments and generate Chinese charts")
    p_bench.add_argument("--output", default="output/benchmarks")
    p_bench.add_argument("--repeat", type=int, default=8)
    p_bench.add_argument("--dataset-file", help="Local dataset file path, recommended: Kaggle CSV/TXT/JSON")

    return parser.parse_args()


def command_init(state_path: Path) -> None:
    system = RevocableAccessSystem.initialize(state_path)
    print(f"initialized {system.state.system_id} at {state_path}")


def command_add_user(state_path: Path, user: str, attrs: list[str]) -> None:
    system = RevocableAccessSystem(state_path)
    record = system.add_user(user, attrs)
    print(f"user={record.user_id} epoch={record.issued_epoch} attrs={','.join(record.attributes)}")


def command_encrypt(state_path: Path, owner: str, dataset: str, policy: str, input_path: Path, output_path: Path) -> None:
    system = RevocableAccessSystem(state_path)
    plaintext = input_path.read_bytes()
    t0 = time.perf_counter()
    offline = system.offline_prepare()
    t1 = time.perf_counter()
    ciphertext = system.encrypt(owner, dataset, policy, plaintext, offline)
    t2 = time.perf_counter()
    write_json(output_path, ciphertext)
    print(f"offline_prepare_ms={(t1 - t0) * 1000:.3f}")
    print(f"online_encrypt_ms={(t2 - t1) * 1000:.3f}")
    print(f"ciphertext={output_path}")


def command_decrypt(state_path: Path, user: str, cipher_path: Path, output_path: Path | None) -> None:
    system = RevocableAccessSystem(state_path)
    ciphertext = read_json(cipher_path)
    t0 = time.perf_counter()
    transformed = system.outsourced_transform(user, ciphertext)
    t1 = time.perf_counter()
    plaintext = system.finalize_decrypt(user, ciphertext, transformed)
    t2 = time.perf_counter()
    if output_path:
        output_path.write_bytes(plaintext)
        destination = str(output_path)
    else:
        destination = "<stdout>"
        sys.stdout.buffer.write(plaintext)
        sys.stdout.buffer.write(b"\n")
    print(f"outsourced_transform_ms={(t1 - t0) * 1000:.3f}", file=sys.stderr)
    print(f"finalize_decrypt_ms={(t2 - t1) * 1000:.3f}", file=sys.stderr)
    print(f"plaintext={destination}", file=sys.stderr)


def command_revoke(state_path: Path, user: str, dataset: str) -> None:
    system = RevocableAccessSystem(state_path)
    system.revoke_user(user, dataset)
    print(f"revoked {user}; attr_epoch={system.state.attr_epoch}; dataset_epoch={system.state.datasets[dataset].data_epoch}")


def command_rewrap(state_path: Path, cipher_path: Path, output_path: Path | None) -> None:
    system = RevocableAccessSystem(state_path)
    ciphertext = read_json(cipher_path)
    rewrapped = system.rewrap_ciphertext(ciphertext)
    target = output_path or cipher_path
    write_json(target, rewrapped)
    print(f"rewrapped={target} data_epoch={rewrapped['metadata']['data_epoch']}")


def command_demo(state_path: Path) -> None:
    if state_path.exists():
        state_path.unlink()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    system = RevocableAccessSystem.initialize(state_path)
    system.add_user("alice", ["role:engineer", "dept:plant1", "clearance:high"])
    system.add_user("bob", ["role:auditor", "dept:plant2"])

    sample_path = state_path.parent / "sample.txt"
    cipher_path = state_path.parent / "cipher.json"
    sample_path.write_text("temperature=82.5\npressure=1.41\nstatus=stable\n", encoding="utf-8")

    offline = system.offline_prepare()
    ciphertext = system.encrypt(
        owner_id="sensor-gateway-01",
        dataset_id="reactor-A",
        policy="(role:engineer AND dept:plant1) AND NOT contractor",
        plaintext=sample_path.read_bytes(),
        offline_token=offline,
    )
    write_json(cipher_path, ciphertext)

    transformed = system.outsourced_transform("alice", ciphertext)
    plaintext = system.finalize_decrypt("alice", ciphertext, transformed).decode("utf-8")
    print("before_revocation:")
    print(plaintext.strip())

    system.revoke_user("alice", "reactor-A")
    ciphertext = system.rewrap_ciphertext(ciphertext)
    write_json(cipher_path, ciphertext)
    try:
        system.outsourced_transform("alice", ciphertext)
        print("unexpected: alice still decrypts")
    except Exception as exc:
        print(f"after_revocation: blocked ({exc})")

    try:
        system.outsourced_transform("bob", ciphertext)
        print("unexpected: bob satisfies policy")
    except Exception as exc:
        print(f"bob_access: blocked ({exc})")

    print(f"demo_state={state_path.parent}")


def command_benchmark(output_dir: Path, repeat: int, dataset_file: Path | None) -> None:
    runner = BenchmarkRunner(output_dir, repeat=repeat, dataset_file=dataset_file)
    root = runner.run()
    print(f"benchmark_output={root}")
    print(f"figures={root / 'figures'}")
    print(f"data={root / 'data'}")


def main() -> None:
    args = parse_args()
    if args.command == "init":
        command_init(Path(args.state))
    elif args.command == "add-user":
        command_add_user(Path(args.state), args.user, args.attrs)
    elif args.command == "encrypt":
        command_encrypt(Path(args.state), args.owner, args.dataset, args.policy, Path(args.input), Path(args.output))
    elif args.command == "decrypt":
        command_decrypt(Path(args.state), args.user, Path(args.cipher), Path(args.output) if args.output else None)
    elif args.command == "revoke-user":
        command_revoke(Path(args.state), args.user, args.dataset)
    elif args.command == "rewrap":
        command_rewrap(Path(args.state), Path(args.cipher), Path(args.output) if args.output else None)
    elif args.command == "demo":
        command_demo(Path(args.state))
    elif args.command == "benchmark":
        command_benchmark(Path(args.output), args.repeat, Path(args.dataset_file) if args.dataset_file else None)


if __name__ == "__main__":
    main()

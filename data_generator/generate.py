"""Главный скрипт генерации данных NeoBank.

Запуск:
    python -m data_generator.generate
"""

import sys
import time
from pathlib import Path

import numpy as np
import yaml

from data_generator.dirt import apply_dirt
from data_generator.generators.accounts import generate_accounts
from data_generator.generators.cards import generate_cards
from data_generator.generators.clients import generate_clients, finalize_clients_status
from data_generator.generators.dimensions import generate_all_dimensions
from data_generator.generators.events import generate_events
from data_generator.generators.experiments import generate_experiments
from data_generator.generators.fraud import generate_fraud
from data_generator.generators.products import generate_products
from data_generator.generators.transactions import generate_transactions
from data_generator.loader import load_all_to_raw


def load_config() -> dict:
    """Читает config.yaml из папки data_generator."""
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        print(f"ERROR: config.yaml not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    config = load_config()

    seed = int(config["seed"])
    n_clients = int(config["scale"]["clients"])
    batch_size = int(config["scale"]["batch_size"])
    start_date = config["period"]["start_date"]
    end_date = config["period"]["end_date"]

    rng = np.random.default_rng(seed)

    print("=== NeoBank Data Generator ===")
    print(f"Clients: {n_clients:,}")
    print(f"Period:  {start_date} — {end_date}")
    print(f"Seed:    {seed}")
    print()

    t0 = time.time()

    print("[1/9] Dimensions...")
    dims = generate_all_dimensions(start_date, end_date)

    print("[2/9] Clients...")
    clients = generate_clients(
        n_clients, start_date, end_date, rng,
        dims["geography"], dims["channels"],
    )
    clients = finalize_clients_status(clients, end_date, rng)

    print("[3/9] Products (cross-sell)...")
    products = generate_products(clients, rng, end_date)

    print("[4/9] Accounts...")
    accounts = generate_accounts(clients, products, rng, end_date)

    print("[5/9] Cards...")
    cards = generate_cards(clients, products, rng, end_date)

    print("[6/9] Transactions...")
    transactions = generate_transactions(clients, products, rng, end_date)

    print("[7/9] Events...")
    events = generate_events(clients, products, transactions, rng, end_date)

    print("[8/9] Fraud...")
    fraud = generate_fraud(transactions, rng, end_date)

    print("[9/9] A/B experiments...")
    experiments, assignments = generate_experiments(clients, rng, start_date, end_date)

    print()
    print("[Dirt] Applying dirt to raw data...")
    data = {
        "dim_channels": dims["channels"],
        "dim_geography": dims["geography"],
        "dim_products": dims["products"],
        "dim_dates": dims["dates"],
        "raw_clients": clients,
        "raw_accounts": accounts,
        "raw_cards": cards,
        "raw_products": products,
        "raw_transactions": transactions,
        "raw_events": events,
        "raw_fraud": fraud,
        "raw_experiments": experiments,
        "raw_ab_assignments": assignments,
    }
    data = apply_dirt(data, rng)

    print()
    print("[Load] Loading to Postgres (schema: raw)...")
    load_all_to_raw(data, config["database"], batch_size)

    elapsed = time.time() - t0
    print()
    print(f"=== Done in {elapsed:.1f} seconds ===")
    print()
    print("Summary:")
    print(f"  Clients:          {len(data['raw_clients']):>10,}")
    print(f"  Accounts:         {len(data['raw_accounts']):>10,}")
    print(f"  Cards:            {len(data['raw_cards']):>10,}")
    print(f"  Products:         {len(data['raw_products']):>10,}")
    print(f"  Transactions:     {len(data['raw_transactions']):>10,}")
    print(f"  Events:           {len(data['raw_events']):>10,}")
    print(f"  Fraud:            {len(data['raw_fraud']):>10,}")
    print(f"  Experiments:      {len(data['raw_experiments']):>10}")
    print(f"  A/B assignments:  {len(data['raw_ab_assignments']):>10,}")


if __name__ == "__main__":
    main()

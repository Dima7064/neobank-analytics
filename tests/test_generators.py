from data_generator.generators.dimensions import generate_dim_channels, generate_dim_products, generate_dim_dates

def test_dimensions():
    """Проверяем, что справочники генерируются с правильным количеством строк и колонок."""
    channels = generate_dim_channels()
    assert len(channels) == 5
    assert "channel_name" in channels.columns

    products = generate_dim_products()
    assert len(products) == 5
    # Проверяем, что вклад (deposit) находится на 3-й позиции (индекс 2)
    assert products.iloc[2]["product_type"] == "deposit"

    dates = generate_dim_dates("2024-01-01", "2024-12-31")
    assert len(dates) == 366  # 2024 год — високосный
    assert dates.iloc[0]["year"] == 2024

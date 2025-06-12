    # Generate mock data from scratch or enrich existing data by prompting an LLM.

    # Args:
    #     tables (dict[str, dict]): The table specifications to generate mock data for. See examples for usage.
    #     sample_size (int | dict[str, int]): The number of rows to generate for each subject table.
    #         If a single integer is provided, the same number of rows will be generated for each subject table.
    #         If a dictionary is provided, the number of rows to generate for each subject table can be specified individually.
    #         Default is 10. Ignored if existing_data is provided.
    #         If a table has a foreign key, the sample size is determined by the corresponding foreign key prompt. If nothing specified, a few rows per parent record are generated.
    #     existing_data (dict[str, pd.DataFrame] | None): Existing data to augment. If provided, the sample_size argument is ignored.
    #         Default is None.
    #     model (str): The LiteLLM chat completion model to be used. Model needs to support structured output / JSON mode.
    #         Examples include:
    #         - `openai/gpt-4.1-nano` (default; fast, and smart)
    #         - `openai/gpt-4.1-mini` (slower, but smarter)
    #         - `openai/gpt-4.1` (slowest, but smartest)
    #         - `gemini/gemini-2.0-flash`
    #         - `gemini/gemini-2.5-flash-preview-04-17`
    #         - 'groq/gemma2-9b-it`
    #         - `groq/llama-3.3-70b-versatile`
    #         - `anthropic/claude-3-7-sonnet-latest`
    #         See https://docs.litellm.ai/docs/providers/ for more options.
    #     api_key (str | None): The API key to use for the LLM. If not provided, LiteLLM will take it from the environment variables.
    #     temperature (float): The temperature to use for the LLM. Default is 1.0.
    #     top_p (float): The top-p value to use for the LLM. Default is 0.95.
    #     return_type (Literal["auto", "dict"]): The format of the returned data. Default is "auto".

    # Returns:
    #     - pd.DataFrame: A single DataFrame containing the generated mock data, if only one table is provided.
    #     - dict[str, pd.DataFrame]: A dictionary containing the generated mock data for each table, if multiple tables are provided.

    # Example of generating mock data for a single table (without PK):
    # ```python
    # from mostlyai import mock

    # tables = {
    #     "guests": {
    #         "prompt": "Guests of an Alpine ski hotel in Austria",
    #         "columns": {
    #             "nationality": {"prompt": "2-letter code for the nationality", "dtype": "string"},
    #             "name": {"prompt": "first name and last name of the guest", "dtype": "string"},
    #             "gender": {"dtype": "category", "values": ["male", "female"]},
    #             "age": {"prompt": "age in years; min: 18, max: 80; avg: 25", "dtype": "integer"},
    #             "date_of_birth": {"prompt": "date of birth", "dtype": "date"},
    #             "checkin_time": {"prompt": "the check in timestamp of the guest; may 2025", "dtype": "datetime"},
    #             "is_vip": {"prompt": "is the guest a VIP", "dtype": "boolean"},
    #             "price_per_night": {"prompt": "price paid per night, in EUR", "dtype": "float"},
    #             "room_number": {"prompt": "room number", "dtype": "integer", "values": [101, 102, 103, 201, 202, 203, 204]}
    #         },
    #     }
    # }
    # df = mock.sample(tables=tables, sample_size=10, model="openai/gpt-4.1-nano")
    # ```

    # Example of generating mock data for multiple tables (with PK/FK relationships):
    # ```python
    # from mostlyai import mock

    # tables = {
    #     "customers": {
    #         "prompt": "Customers of a hardware store",
    #         "columns": {
    #             "customer_id": {"prompt": "the unique id of the customer", "dtype": "integer"},
    #             "name": {"prompt": "first name and last name of the customer", "dtype": "string"},
    #         },
    #         "primary_key": "customer_id",  # single string; no composite keys allowed
    #     },
    #     "warehouses": {
    #         "prompt": "Warehouses of a hardware store",
    #         "columns": {
    #             "warehouse_id": {"prompt": "the unique id of the warehouse", "dtype": "integer"},
    #             "name": {"prompt": "the name of the warehouse", "dtype": "string"},
    #         },
    #         "primary_key": "warehouse_id",
    #     },
    #     "orders": {
    #         "prompt": "Orders of a Customer",
    #         "columns": {
    #             "customer_id": {"prompt": "the customer id for that order", "dtype": "integer"},
    #             "warehouse_id": {"prompt": "the warehouse id for that order", "dtype": "integer"},
    #             "order_id": {"prompt": "the unique id of the order", "dtype": "string"},
    #             "text": {"prompt": "order text description", "dtype": "string"},
    #             "amount": {"prompt": "order amount in USD", "dtype": "float"},
    #         },
    #         "primary_key": "order_id",
    #         "foreign_keys": [
    #             {
    #                 "column": "customer_id",
    #                 "referenced_table": "customers",
    #                 "prompt": "each customer has anywhere between 2 and 3 orders",
    #             },
    #             {
    #                 "column": "warehouse_id",
    #                 "referenced_table": "warehouses",
    #             },
    #         ],
    #     },
    #     "items": {
    #         "prompt": "Items in an Order",
    #         "columns": {
    #             "item_id": {"prompt": "the unique id of the item", "dtype": "string"},
    #             "order_id": {"prompt": "the order id for that item", "dtype": "string"},
    #             "name": {"prompt": "the name of the item", "dtype": "string"},
    #             "price": {"prompt": "the price of the item in USD", "dtype": "float"},
    #         },
    #         "foreign_keys": [
    #             {
    #                 "column": "order_id",
    #                 "referenced_table": "orders",
    #                 "prompt": "each order has between 1 and 2 items",
    #             }
    #         ],
    #     },
    # }
    # data = mock.sample(tables=tables, sample_size=2, model="openai/gpt-4.1")
    # df_customers = data["customers"]
    # df_warehouses = data["warehouses"]
    # df_orders = data["orders"]
    # df_items = data["items"]
    # ```

    # Example of enriching a single dataframe:
    # ```python
    # from mostlyai import mock
    # import pandas as pd

    # tables = {
    #     "patients": {
    #         "prompt": "Patients of a hospital in Finland",
    #         "columns": {
    #             "full_name": {"prompt": "first name and last name of the patient", "dtype": "string"},
    #             "date_of_birth": {"prompt": "date of birth", "dtype": "date"},
    #             "place_of_birth": {"prompt": "place of birth", "dtype": "string"},
    #         },
    #     },
    # }
    # existing_df = pd.DataFrame({
    #     "age": [25, 30, 35, 40],
    #     "gender": ["male", "male", "female", "female"],
    # })
    # enriched_df = mock.sample(
    #     tables=tables,
    #     existing_data={"patients": existing_df},
    #     model="openai/gpt-4.1-nano"
    # )
    # enriched_df
    # ```

    # Example of enriching / augmenting an existing dataset:
    # ```python
    # from mostlyai import mock
    # import pandas as pd

    # tables = {
    #     "customers": {
    #         "prompt": "Customers of a hardware store",
    #         "columns": {
    #             "customer_id": {"prompt": "the unique id of the customer", "dtype": "integer"},
    #             "name": {"prompt": "first name and last name of the customer", "dtype": "string"},
    #             "email": {"prompt": "email address of the customer", "dtype": "string"},
    #             "phone": {"prompt": "phone number of the customer", "dtype": "string"},
    #             "loyalty_level": {"dtype": "category", "values": ["bronze", "silver", "gold", "platinum"]},
    #         },
    #         "primary_key": "customer_id",
    #     },
    #     "orders": {
    #         "prompt": "Orders of a Customer",
    #         "columns": {
    #             "order_id": {"prompt": "the unique id of the order", "dtype": "string"},
    #             "customer_id": {"prompt": "the customer id for that order", "dtype": "integer"},
    #             "order_date": {"prompt": "the date when the order was placed", "dtype": "date"},
    #             "total_amount": {"prompt": "order amount in USD", "dtype": "float"},
    #             "status": {"dtype": "category", "values": ["pending", "shipped", "delivered", "cancelled"]},
    #         },
    #         "primary_key": "order_id",
    #         "foreign_keys": [
    #             {
    #                 "column": "customer_id",
    #                 "referenced_table": "customers",
    #                 "prompt": "each customer has anywhere between 1 and 3 orders",
    #             },
    #         ],
    #     },
    # }
    # existing_customers = pd.DataFrame({
    #     "customer_id": [101, 102, 103],
    #     "name": ["John Davis", "Maria Garcia", "Wei Chen"],
    # })
    # existing_orders = pd.DataFrame({
    #     "order_id": ["ORD-001", "ORD-002"],
    #     "customer_id": [101, 101],
    # })
    # data = mock.sample(
    #     tables=tables,
    #     existing_data={
    #         "customers": existing_customers,
    #         "orders": existing_orders,
    #     },
    #     model="openai/gpt-4.1-nano"
    # )
    # df_customers = data["customers"]
    # df_orders = data["orders"]
    # ```
from mostlyai import mock

# print(mock.sample.__doc__)

# Define schema for Users, Staff, Tables, MenuItems, Coupons, Orders
# We'll use integer PKs and set up FKs for relationships

tables = {
    "users": {
        "prompt": "Customers of a restaurant",
        "columns": {
            "user_id": {"prompt": "unique user id", "dtype": "integer"},
            "name": {"prompt": "full name of the user", "dtype": "string"},
            "email": {"prompt": "email address", "dtype": "string"},
            "phone": {"prompt": "phone number", "dtype": "string"},
        },
        "primary_key": "user_id",
    },
    "staff": {
        "prompt": "Staff members of a restaurant (waiters, managers)",
        "columns": {
            "staff_id": {"prompt": "unique staff id", "dtype": "integer"},
            "name": {"prompt": "full name of the staff", "dtype": "string"},
            "role": {"dtype": "category", "values": ["waiter", "manager"]},
        },
        "primary_key": "staff_id",
    },
    "tables": {
        "prompt": "Restaurant tables",
        "columns": {
            "table_id": {"prompt": "unique table id", "dtype": "integer"},
            "table_number": {"prompt": "table number", "dtype": "integer"},
            "seats": {"prompt": "number of seats at the table", "dtype": "integer"},
        },
        "primary_key": "table_id",
    },
    "menu_items": {
        "prompt": "Menu items (food and drinks) at a restaurant",
        "columns": {
            "item_id": {"prompt": "unique menu item id", "dtype": "integer"},
            "name": {"prompt": "name of the menu item", "dtype": "string"},
            "category": {"dtype": "category", "values": ["food", "drink", "dessert"]},
            "price": {"prompt": "price in USD", "dtype": "float"},
        },
        "primary_key": "item_id",
    },
    "coupons": {
        "prompt": "Discount coupons for restaurant customers",
        "columns": {
            "coupon_id": {"prompt": "unique coupon id", "dtype": "integer"},
            "code": {"prompt": "coupon code", "dtype": "string"},
            "discount_percent": {"prompt": "discount percentage", "dtype": "integer"},
            "valid_until": {"prompt": "coupon valid until date", "dtype": "date"},
        },
        "primary_key": "coupon_id",
    },
    "orders": {
        "prompt": "Orders placed by users at a restaurant, with tips, assigned waiter, table, coupon, payment, and timestamp",
        "columns": {
            "order_id": {"prompt": "unique order id", "dtype": "integer"},
            "user_id": {"prompt": "user id who placed the order", "dtype": "integer"},
            "staff_id": {"prompt": "waiter staff id assigned to the order", "dtype": "integer"},
            "table_id": {"prompt": "table id assigned to the order", "dtype": "integer"},
            "coupon_id": {"prompt": "coupon id applied to the order (nullable)", "dtype": "integer"},
            "total_amount": {"prompt": "total order amount in USD (after discount)", "dtype": "float"},
            "tip": {"prompt": "tip amount in USD", "dtype": "float"},
            "payment_method": {"dtype": "category", "values": ["cash", "credit_card", "mobile"]},
            "timestamp": {"prompt": "order timestamp (ISO format)", "dtype": "datetime"},
        },
        "primary_key": "order_id",
        "foreign_keys": [
            {"column": "user_id", "referenced_table": "users"},
            {"column": "staff_id", "referenced_table": "staff"},
            {"column": "table_id", "referenced_table": "tables"},
            {"column": "coupon_id", "referenced_table": "coupons", "prompt": "some orders have a coupon, some do not"},
        ],
    },
    "order_items": {
        "prompt": "Items in each order (many-to-many between orders and menu items)",
        "columns": {
            "order_item_id": {"prompt": "unique order item id", "dtype": "integer"},
            "order_id": {"prompt": "order id", "dtype": "integer"},
            "item_id": {"prompt": "menu item id", "dtype": "integer"},
            "quantity": {"prompt": "quantity of the item in the order", "dtype": "integer"},
        },
        "primary_key": "order_item_id",
        "foreign_keys": [
            {"column": "order_id", "referenced_table": "orders"},
            {"column": "item_id", "referenced_table": "menu_items"},
        ],
    },
}

# Generate a small sample (4 users, 2 staff, 3 tables, 6 menu items, 2 coupons, 5 orders)
sample_size = {
    "users": 4,
    "staff": 2,
    "tables": 3,
    "menu_items": 6,
    "coupons": 2,
    "orders": 5,
    "order_items": 12,
}

mock_data = mock.sample(tables=tables, sample_size=sample_size, model="litellm_proxy/openai/gpt-4.1-nano")

# Save each collection as CSV for inspection
for name, df in mock_data.items():
    df.to_csv(f"/mnt/data/{name}.csv", index=False)

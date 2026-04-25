class TableRelationships:

    relationships = [

        {
            "left_table": "customers",
            "right_table": "orders",
            "left_key": "user_id",
            "right_key": "user_id"
        },

        {
            "left_table": "orders",
            "right_table": "orderdetails",
            "left_key": "order_id",
            "right_key": "order_id"
        },

        {
            "left_table": "orders",
            "right_table": "transactions",
            "left_key": "order_id",
            "right_key": "order_id"
        },

        {
            "left_table": "products",
            "right_table": "orderdetails",
            "left_key": "product_id",
            "right_key": "product_id"
        },

        {
            "left_table": "products",
            "right_table": "categories",
            "left_key": "category_id",
            "right_key": "category_id"
        },

        {
            "left_table": "customers",
            "right_table": "visits",
            "left_key": "user_id",
            "right_key": "customer_id"
        },

        {
            "left_table": "customers",
            "right_table": "consultation",
            "left_key": "user_id",
            "right_key": "customer_id"
        }

    ]

    @classmethod
    def get_relationships(cls):
        return cls.relationships

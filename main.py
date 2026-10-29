import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class SunglassesProfitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт доходности солнцезащитных очков — ИП «Дудин Д.А.»")
        self.root.geometry("1280x720")

        self.conn = sqlite3.connect("sunglasses.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        self.create_widgets()
        self.load_models()

    # ---------------------- БАЗА ДАННЫХ ----------------------
    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sunglasses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT,
                article TEXT,
                supplier TEXT,
                lens_color TEXT,
                frame_type TEXT,
                wholesale_price REAL NOT NULL,
                retail_price REAL NOT NULL,
                qty_purchased INTEGER NOT NULL DEFAULT 0,
                qty_sold INTEGER NOT NULL DEFAULT 0,
                qty_planned INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sunglasses_name
            ON sunglasses(name)
        """)
        self.conn.commit()

    # ---------------------- ИНТЕРФЕЙС ----------------------
    def create_widgets(self):
        input_frame = tk.LabelFrame(
            self.root, text="Добавление новой модели солнцезащитных очков",
            padx=10, pady=10
        )
        input_frame.pack(fill="x", padx=10, pady=8)

        # ---- Строка 0: модель, бренд, артикул ----
        tk.Label(input_frame, text="Модель очков:").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_name = tk.Entry(input_frame, width=28)
        self.entry_name.grid(row=0, column=1, pady=3, padx=5)

        tk.Label(input_frame, text="Бренд:").grid(row=0, column=2, sticky="w", pady=3, padx=(15, 0))
        self.entry_brand = tk.Entry(input_frame, width=18)
        self.entry_brand.grid(row=0, column=3, pady=3, padx=5)

        tk.Label(input_frame, text="Артикул:").grid(row=0, column=4, sticky="w", pady=3, padx=(15, 0))
        self.entry_article = tk.Entry(input_frame, width=18)
        self.entry_article.grid(row=0, column=5, pady=3, padx=5)

        # ---- Строка 1: поставщик, цвет линз, тип оправы ----
        tk.Label(input_frame, text="Поставщик:").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_supplier = tk.Entry(input_frame, width=28)
        self.entry_supplier.grid(row=1, column=1, pady=3, padx=5)

        tk.Label(input_frame, text="Цвет линз:").grid(row=1, column=2, sticky="w", pady=3, padx=(15, 0))
        self.combo_lens = ttk.Combobox(
            input_frame, width=16,
            values=["Серые", "Коричневые", "Зелёные", "Голубые",
                    "Розовые", "Жёлтые", "Зеркальные", "Градиентные", "Фотохромные"]
        )
        self.combo_lens.grid(row=1, column=3, pady=3, padx=5)

        tk.Label(input_frame, text="Тип оправы:").grid(row=1, column=4, sticky="w", pady=3, padx=(15, 0))
        self.combo_frame = ttk.Combobox(
            input_frame, width=16,
            values=["Пластик", "Металл", "Комбинированная",
                    "Без оправы", "Полуободковая", "Ободковая"]
        )
        self.combo_frame.grid(row=1, column=5, pady=3, padx=5)

        # ---- Строка 2: цены ----
        tk.Label(input_frame, text="Оптовая цена (руб.):").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_wholesale = tk.Entry(input_frame, width=15)
        self.entry_wholesale.grid(row=2, column=1, pady=3, padx=5, sticky="w")

        tk.Label(input_frame, text="Розничная цена (руб.):").grid(
            row=2, column=2, sticky="w", pady=3, padx=(15, 0)
        )
        self.entry_retail = tk.Entry(input_frame, width=15)
        self.entry_retail.grid(row=2, column=3, pady=3, padx=5, sticky="w")

        # ---- Строка 3: количества ----
        tk.Label(input_frame, text="Закуплено (шт.):").grid(row=3, column=0, sticky="w", pady=3)
        self.entry_purchased = tk.Entry(input_frame, width=15)
        self.entry_purchased.grid(row=3, column=1, pady=3, padx=5, sticky="w")

        tk.Label(input_frame, text="Продано (шт.):").grid(
            row=3, column=2, sticky="w", pady=3, padx=(15, 0)
        )
        self.entry_sold = tk.Entry(input_frame, width=15)
        self.entry_sold.grid(row=3, column=3, pady=3, padx=5, sticky="w")

        tk.Label(input_frame, text="К докупке (шт.):").grid(
            row=3, column=4, sticky="w", pady=3, padx=(15, 0)
        )
        self.entry_planned = tk.Entry(input_frame, width=15)
        self.entry_planned.grid(row=3, column=5, pady=3, padx=5, sticky="w")

        # ---- Кнопка добавления ----
        btn_add = tk.Button(
            input_frame, text="Добавить модель",
            command=self.add_model,
            bg="#FF9800", fg="white",
            font=("Arial", 10, "bold"), padx=20
        )
        btn_add.grid(row=4, column=0, columnspan=6, pady=10)

        # ===== Таблица =====
        list_frame = tk.LabelFrame(
            self.root, text="Список солнцезащитных очков и расчёт доходности",
            padx=10, pady=10
        )
        list_frame.pack(fill="both", expand=True, padx=10, pady=8)

        btns_frame = tk.Frame(list_frame)
        btns_frame.pack(fill="x", pady=(0, 8))

        tk.Button(btns_frame, text="Обновить список", command=self.load_models, padx=10).pack(side="left", padx=3)
        tk.Button(btns_frame, text="Сортировать по прибыли", command=self.sort_by_profit, padx=10).pack(side="left", padx=3)
        tk.Button(btns_frame, text="Сортировать по окупаемости", command=self.sort_by_payback, padx=10).pack(side="left", padx=3)
        tk.Button(
            btns_frame, text="Удалить выбранную модель",
            command=self.delete_model, padx=10, bg="#e53935", fg="white"
        ).pack(side="left", padx=3)

        self.total_label = tk.Label(
            btns_frame, text="", font=("Arial", 10, "bold"), fg="#1565C0"
        )
        self.total_label.pack(side="right", padx=10)

        columns = (
            "id", "name", "brand", "article", "supplier", "lens", "frame",
            "wholesale", "retail",
            "purchased", "sold", "planned",
            "revenue", "cost", "profit",
            "profit_pct", "payback_pct", "stock", "need_buy_sum",
        )
        headings = {
            "id": "ID", "name": "Модель", "brand": "Бренд", "article": "Артикул",
            "supplier": "Поставщик", "lens": "Цвет линз", "frame": "Тип оправы",
            "wholesale": "Опт. цена", "retail": "Розн. цена",
            "purchased": "Закуплено", "sold": "Продано", "planned": "К докупке",
            "revenue": "Выручка", "cost": "Затраты", "profit": "Прибыль",
            "profit_pct": "% приб.", "payback_pct": "% окуп.",
            "stock": "Остаток", "need_buy_sum": "Сумма докупки",
        }
        widths = {
            "id": 40, "name": 150, "brand": 90, "article": 80, "supplier": 100,
            "lens": 90, "frame": 100,
            "wholesale": 80, "retail": 80,
            "purchased": 80, "sold": 70, "planned": 80,
            "revenue": 90, "cost": 90, "profit": 90,
            "profit_pct": 70, "payback_pct": 70, "stock": 70, "need_buy_sum": 100,
        }

        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=18)
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        sy = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure("low_profit", background="#FFEBEE")
        self.tree.tag_configure("high_profit", background="#E8F5E9")
        self.tree.tag_configure("not_payback", background="#FFF3E0")

    # ---------------------- ВАЛИДАЦИЯ ----------------------
    @staticmethod
    def parse_float(value, field_name, allow_empty=False):
        value = value.strip().replace(",", ".")
        if not value:
            if allow_empty:
                return 0.0
            raise ValueError(f"Поле «{field_name}» не заполнено.")
        try:
            result = float(value)
        except ValueError:
            raise ValueError(f"Поле «{field_name}» должно быть числом.")
        if result < 0:
            raise ValueError(f"Поле «{field_name}» не может быть отрицательным.")
        return result

    @staticmethod
    def parse_int(value, field_name, allow_empty=False):
        value = value.strip()
        if not value:
            if allow_empty:
                return 0
            raise ValueError(f"Поле «{field_name}» не заполнено.")
        try:
            result = int(value)
        except ValueError:
            raise ValueError(f"Поле «{field_name}» должно быть целым числом.")
        if result < 0:
            raise ValueError(f"Поле «{field_name}» не может быть отрицательным.")
        return result

    # ---------------------- ДОБАВЛЕНИЕ ----------------------
    def add_model(self):
        try:
            name = self.entry_name.get().strip()
            if not name:
                raise ValueError("Поле «Модель очков» не заполнено.")

            brand = self.entry_brand.get().strip()
            article = self.entry_article.get().strip()
            supplier = self.entry_supplier.get().strip()
            lens_color = self.combo_lens.get().strip()
            frame_type = self.combo_frame.get().strip()

            wholesale = self.parse_float(self.entry_wholesale.get(), "Оптовая цена")
            retail = self.parse_float(self.entry_retail.get(), "Розничная цена")

            if retail <= wholesale:
                raise ValueError(
                    "Розничная цена должна быть больше оптовой, "
                    "иначе модель убыточна."
                )

            purchased = self.parse_int(self.entry_purchased.get(), "Закуплено", allow_empty=True)
            sold = self.parse_int(self.entry_sold.get(), "Продано", allow_empty=True)
            planned = self.parse_int(self.entry_planned.get(), "К докупке", allow_empty=True)

            if sold > purchased:
                raise ValueError(
                    "Количество проданных единиц не может превышать "
                    "количество закупленных."
                )
        except ValueError as e:
            messagebox.showwarning("Ошибка ввода", str(e))
            return

        self.cursor.execute("""
            INSERT INTO sunglasses
                (name, brand, article, supplier, lens_color, frame_type,
                 wholesale_price, retail_price,
                 qty_purchased, qty_sold, qty_planned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, brand, article, supplier, lens_color, frame_type,
            wholesale, retail, purchased, sold, planned
        ))
        self.conn.commit()

        messagebox.showinfo("Успех", f"Модель «{name}» успешно добавлена.")
        self.clear_inputs()
        self.load_models()

    def clear_inputs(self):
        for entry in (
            self.entry_name, self.entry_brand, self.entry_article,
            self.entry_supplier, self.entry_wholesale, self.entry_retail,
            self.entry_purchased, self.entry_sold, self.entry_planned,
        ):
            entry.delete(0, tk.END)
        self.combo_lens.set("")
        self.combo_frame.set("")

    # ---------------------- РАСЧЁТ ----------------------
    @staticmethod
    def calc_row(row):
        (mid, name, brand, article, supplier, lens_color, frame_type,
         wholesale, retail, purchased, sold, planned) = row

        revenue = sold * retail
        cost = sold * wholesale
        profit = revenue - cost
        profit_pct = (profit / revenue * 100) if revenue > 0 else 0.0

        total_purchase_cost = purchased * wholesale
        if total_purchase_cost > 0:
            payback_pct = min(revenue / total_purchase_cost * 100, 999.99)
        else:
            payback_pct = 0.0

        stock = purchased - sold
        need_buy_sum = planned * wholesale

        return (
            round(revenue, 2), round(cost, 2), round(profit, 2),
            round(profit_pct, 2), round(payback_pct, 2),
            stock, round(need_buy_sum, 2),
        )

    # ---------------------- СПИСОК ----------------------
    def load_models(self, order_by="id", reverse=False):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cursor.execute("""
            SELECT id, name, brand, article, supplier, lens_color, frame_type,
                   wholesale_price, retail_price,
                   qty_purchased, qty_sold, qty_planned
            FROM sunglasses
        """)
        rows = self.cursor.fetchall()

        data = []
        total_profit = 0.0
        for row in rows:
            calc = self.calc_row(row)
            total_profit += calc[2]
            data.append((row, calc))

        key_funcs = {
            "id": lambda x: x[0][0],
            "name": lambda x: x[0][1].lower(),
            "profit": lambda x: x[1][2],
            "payback": lambda x: x[1][4],
        }
        data.sort(key=key_funcs.get(order_by, key_funcs["id"]), reverse=reverse)

        for row, calc in data:
            (mid, name, brand, article, supplier, lens_color, frame_type,
             wholesale, retail, purchased, sold, planned) = row
            (revenue, cost, profit, profit_pct, payback_pct,
             stock, need_buy_sum) = calc

            tags = ()
            if profit_pct < 20:
                tags = ("low_profit",)
            elif profit_pct >= 50:
                tags = ("high_profit",)
            if payback_pct < 100 and sold > 0:
                tags = tags + ("not_payback",)

            self.tree.insert("", "end", values=(
                mid, name, brand or "—", article or "—", supplier or "—",
                lens_color or "—", frame_type or "—",
                f"{wholesale:.2f}", f"{retail:.2f}",
                purchased, sold, planned,
                f"{revenue:.2f}", f"{cost:.2f}", f"{profit:.2f}",
                f"{profit_pct:.1f}%", f"{payback_pct:.1f}%",
                stock, f"{need_buy_sum:.2f}",
            ), tags=tags)

        self.total_label.config(
            text=f"Общая прибыль по всем моделям: {total_profit:.2f} руб."
        )

    def sort_by_profit(self):
        self.load_models(order_by="profit", reverse=True)

    def sort_by_payback(self):
        self.load_models(order_by="payback", reverse=True)

    # ---------------------- УДАЛЕНИЕ ----------------------
    def delete_model(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Сначала выберите модель для удаления.")
            return

        item = selected[0]
        values = self.tree.item(item, "values")
        mid, name = values[0], values[1]

        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Удалить модель солнцезащитных очков?\n\nID: {mid}\nМодель: {name}"
        )
        if not confirm:
            return

        self.cursor.execute("DELETE FROM sunglasses WHERE id = ?", (mid,))
        self.conn.commit()
        messagebox.showinfo("Успех", f"Модель «{name}» удалена.")
        self.load_models()

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = SunglassesProfitApp(root)
    root.mainloop()
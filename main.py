import pandas as pd
import tkinter as tk
import calculator

df_matt = pd.read_csv('schm_prod_info.csv')

# Create object
win = tk.Tk()
win.title("Supply Chain Module Calculator")
win.configure(padx=20, pady=10)

# Adjust size
win.geometry("1100x500")

# text boxes / labels
# top text box
top_text_font = ("Ariel", 20, "bold")
top_text = tk.Label(text='Material Cost Calculator')
top_text.grid(row=0, column=1, columnspan=4, pady=(0, 5))
top_text.configure(font=top_text_font)

# text box -- product name
prod_type_text = tk.Label(text='Product:')
prod_type_text.grid(row=1, column=1)

# text box -- unit price
uprice_text = tk.Label(text='Unit Price:')
uprice_text.grid(row=2, column=1)

# text box -- quantity
quantity_text = tk.Label(text='Desired Quantity:')
quantity_text.grid(row=3, column=1)

# text box -- quality
quality_text = tk.Label(text='Desired Quality:')
quality_text.grid(row=4, column=1)

# text header -- results
result_head = tk.Label(text='Results')
result_head.grid(row=7, column=1, columnspan=4, pady=(15, 5))
result_head.configure(font=top_text_font)

# label -- supplier names
supp1_text = tk.Label(text='Supplier 1:')
supp1_text.grid(row=8, column=0)

supp2_text = tk.Label(text='Supplier 2:')
supp2_text.grid(row=8, column=2)
supp2_text.configure(padx=10)

# label/text box -- supplier results
supp1_result = tk.Text()
supp1_result.grid(row=8, column=1)
supp1_result.configure(width=45, height=3)

supp2_result = tk.Text()
supp2_result.grid(row=8, column=3)
supp2_result.configure(width=45, height=3)

# informative data
# label/text box -- total price of order
total_price_text = tk.Label(text='Total Price:')
total_price_text.grid(row=10, column=0)

total_price_result = tk.Text()
total_price_result.grid(row=10, column=1)
total_price_result.configure(width=45, height=3)

# label/text box -- total lead time
total_lead_text = tk.Label(text='Total Lead Time:')
total_lead_text.grid(row=10, column=2)
total_lead_text.configure(padx=10)

total_lead_result = tk.Text()
total_lead_result.grid(row=10, column=3)
total_lead_result.configure(width=45, height=3)

# label/text box -- total weight
total_weight_text = tk.Label(text='Total Weight:')
total_weight_text.grid(row=11, column=0)
total_weight_text.configure(padx=10)

total_weight_result = tk.Text()
total_weight_result.grid(row=11, column=1)
total_weight_result.configure(width=45, height=3)

# label/text box -- total cost of shipment
ship_cost_text = tk.Label(text='Shipping Costs:')
ship_cost_text.grid(row=11, column=2)
ship_cost_text.configure(padx=10)

ship_cost_result = tk.Text()
ship_cost_result.grid(row=11, column=3)
ship_cost_result.configure(width=45, height=3)

# label/text box -- total cost of shipment
profit_text = tk.Label(text='Est. Profit Using\nBest Supplier\n(Excluding COP)')
profit_text.grid(row=12, column=2)
profit_text.configure(padx=10)

profit_result = tk.Text()
profit_result.grid(row=12, column=3)
profit_result.configure(width=45, height=3)

# interactable code
# create drop down menu for different products
value_prod_type = tk.StringVar(win)
prod_type = tk.OptionMenu(win, value_prod_type, *df_matt['Name'])
prod_type.grid(row=1, column=2, sticky='ew')
prod_type.configure(width=15)

# create entry box for quantity of products desired
uprice_entry = tk.Entry()
uprice_entry.grid(row=2, column=2)

# create entry box for quantity of products desired
quantity_entry = tk.Entry()
quantity_entry.grid(row=3, column=2)

# create entry box for quality of products desired
quality_entry = tk.Entry()
quality_entry.grid(row=4, column=2)


# create function to clear text boxes
def clear_boxes():
    supp1_result.delete('1.0', 'end')
    supp2_result.delete('1.0', 'end')
    total_price_result.delete('1.0', 'end')
    total_lead_result.delete('1.0', 'end')
    total_weight_result.delete('1.0', 'end')
    ship_cost_result.delete('1.0', 'end')
    profit_result.delete('1.0', 'end')


# create function to update labels with outputted info
def interpret_info():
    # clear boxes
    clear_boxes()

    # retrieve values
    prod_name = value_prod_type.get()
    unit_price = uprice_entry.get()
    quantity = quantity_entry.get()
    quality = quality_entry.get()

    # calculate total revenue
    revenue = int(quantity) * float(unit_price)

    my_calc = calculator.Calculator(prod_name=prod_name, quan=quantity, qual=quality, uprice=unit_price)
    df_suppliers = my_calc.find_supp()
    df_suppliers = df_suppliers.drop_duplicates()
    df_suppliers = df_suppliers[df_suppliers['Total Lead Time'] < 4]
    ship_info = my_calc.find_ship_info()

    df_suppliers = df_suppliers.sort_values(by=['Total Price'])

    supp1_list = df_suppliers['Supplier 1'].iloc[:3].values
    supp1_qlist = df_suppliers['Supplier 1 Quantity'].iloc[:3].values
    supp1_order_amt = df_suppliers['Supplier 1 Num of Orders'].iloc[:3].values

    total_price_list = df_suppliers['Total Price'].iloc[:3].values
    total_lead_list = df_suppliers['Total Lead Time'].iloc[:3].values

    try:
        supp2_list = df_suppliers['Supplier 2'].iloc[:3].values
        supp2_qlist = df_suppliers['Supplier 2 Quantity'].iloc[:3].values
        supp2_order_amt = df_suppliers['Supplier 2 Num of Orders'].iloc[:3].values
    except KeyError:
        for i in range(3):
            supp1_result.insert(tk.END, f'{i + 1}. {supp1_list[i]}: {supp1_qlist[i]} units '
                                        f'({supp1_order_amt[i]} orders)\n')

            total_price_result.insert(tk.END, f'{i + 1}. ${total_price_list[i]}\n')
            total_lead_result.insert(tk.END, f'{i + 1}. {total_lead_list[i]} weeks\n')

            total_weight_result.insert(tk.END, f'{i + 1}. {ship_info[i][0]} lbs\n')
            ship_cost_result.insert(tk.END, f'{i + 1}. {2 - i} weeks: ${ship_info[2 - i][1]}\n')

            profit = revenue - total_price_list[0] - ship_info[2 - i][1]
            profit_result.insert(tk.END, f'{i + 1}. {2 - i} week shipping: ${profit}\n')
    else:
        for i in range(3):
            supp1_result.insert(tk.END, f'{i + 1}. {supp1_list[i]}: {supp1_qlist[i]} units '
                                        f'({supp1_order_amt[i]} orders)\n')
            supp2_result.insert(tk.END, f'{i+1}. {supp2_list[i]}: {supp2_qlist[i]} units '
                                        f'({supp2_order_amt[i]} orders)\n')

            total_price_result.insert(tk.END, f'{i+1}. ${total_price_list[i]}\n')
            total_lead_result.insert(tk.END, f'{i+1}. {total_lead_list[i]} weeks\n')

            total_weight_result.insert(tk.END, f'{i+1}. {ship_info[i][0]} lbs\n')
            ship_cost_result.insert(tk.END, f'{i+1}. {2-i} weeks: ${ship_info[2-i][1]}\n')

            profit = revenue - total_price_list[0] - ship_info[2-i][1]
            profit_result.insert(tk.END, f'{i+1}. {2-i} week shipping: ${profit}\n')


# create button to calculate values
calc_button = tk.Button(win, text='Calculate', command=interpret_info)
calc_button.grid(row=6, column=2)

# Execute tkinter
win.mainloop()

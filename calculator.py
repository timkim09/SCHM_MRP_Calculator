import pandas as pd
import math


class Calculator:
    """ calculator used to determine how much material to order and which suppliers to order from

    Attributes:
        prod_name (str): name of the product to be sold
        quan (int): product quantity to be sold
        qual (int): specified product quality from customer
        uprice (float): unit selling price for a product
    """

    def __init__(self, prod_name, quan, qual, uprice):
        self.df_matt = pd.read_csv('schm_prod_info.csv')
        self.df_supp = pd.read_csv('schm_supp_info.csv')
        self.df_ship = pd.read_csv('schm_ship_info.csv')

        self.df_item = self.df_matt[self.df_matt['Name'] == prod_name]

        self.prod_name = prod_name
        self.quan = int(quan)
        self.qual = int(qual)
        self.uprice = float(uprice)

    def find_supp(self):
        """ calculate the amount of material required for all suppliers in order to reach the desired quantity and
        quality for a specific order

        Returns:
            df_costs (DataFrame): dataframe containing all possible supplier combinations to reach the desired quality
            and quantity amount
        """
        high_qual_supp = list()
        low_qual_supp = list()

        # find the type of material that our specified product is and find the required amount of material used to
        # produce one product
        matt_type = self.df_item['Material Type'].iloc[0]
        req_matt = int(self.df_item['Material'].iloc[0])

        # retrieve all relevant information pertaining to suppliers and save as one item in a list, categorizing
        # each supplier by the quality of the product's material (above or below)
        for supp in self.df_supp[matt_type]:
            if type(supp) == str:
                supp_name = self.df_supp[self.df_supp[matt_type] == supp]['Name'].iloc[0]
                min_lead = int(self.df_supp[self.df_supp[matt_type] == supp]['Min_Lead'].iloc[0])
                min_qty = int(self.df_supp[self.df_supp[matt_type] == supp]['Min_QTY'].iloc[0])
                max_qty = int(self.df_supp[self.df_supp[matt_type] == supp]['Max_QTY'].iloc[0])
                per_matt_price = float(supp.split('/')[0])
                matt_qual = int(supp.split('/')[1])
                if matt_qual >= self.qual:
                    high_qual_supp.append([supp_name, per_matt_price, matt_qual, min_lead, min_qty, max_qty])
                else:
                    low_qual_supp.append([supp_name, per_matt_price, matt_qual, min_lead, min_qty, max_qty])

        df_costs = pd.DataFrame()

        # determine the quantity-quality (aggregate quality of all materials)
        target_total_qual = self.quan * req_matt * self.qual

        if not low_qual_supp:
            for hsupp in high_qual_supp:
                # retrieve all relevant variables pertaining to higher quality supplier
                price = hsupp[1]
                lead_time = hsupp[3]
                minqty = hsupp[4]
                maxqty = hsupp[5]

                matt_quan = req_matt * self.quan
                total_quan = matt_quan

                if self.quan < minqty:
                    total_quan = minqty

                wkdldisc_rate = self.df_supp[self.df_supp['Name'] == hsupp[0]]['DIS_WKDL'].iloc[0]
                num_wkdl = math.ceil(total_quan / maxqty)

                wkdl_disc = 0
                if type(wkdldisc_rate) != float:
                    disc_weeks = int(wkdldisc_rate.split('/')[1])

                    if num_wkdl >= disc_weeks:
                        wkdl_disc = int(wkdldisc_rate.split('/')[0])

                qtydisc_rate = self.df_supp[self.df_supp['Name'] == hsupp[0]]['DIS_QTY'].iloc[0]

                disc_perc = 0
                if type(qtydisc_rate) != float:
                    disc_quan = int(qtydisc_rate.split('/')[1])

                    if disc_quan <= total_quan:
                        disc_perc = int(qtydisc_rate.split('/')[0])

                total_disc = wkdl_disc + disc_perc

                total_price = price * matt_quan * (100 - total_disc) / 100

                total_lead = lead_time + num_wkdl - 1

                supp_dict = {'Supplier 1': [hsupp[0]],
                             'Supplier 1 Quantity': [total_quan],
                             'Supplier 1 Num of Orders': [num_wkdl],
                             'Total Price': [total_price],
                             'Total Lead Time': [total_lead]}
                supp_df = pd.DataFrame(supp_dict)
                df_costs = pd.concat([df_costs, supp_df])

        else:
            # match a higher quality supplier with a lower quality supplier
            for hsupp in high_qual_supp:
                for lsupp in low_qual_supp:
                    # retrieve all relevant variables pertaining to lower quality supplier
                    lsupp_price = lsupp[1]
                    lsupp_qual = lsupp[2]
                    lsupp_lead = lsupp[3]
                    lsupp_minqty = lsupp[4]
                    lsupp_maxqty = lsupp[5]

                    # retrieve all relevant variables pertaining to higher quality supplier
                    hsupp_price = hsupp[1]
                    hsupp_qual = hsupp[2]
                    hsupp_lead = hsupp[3]
                    hsupp_minqty = hsupp[4]
                    hsupp_maxqty = hsupp[5]

                    # find the total amount of material required to produce the total amount of products
                    matt_quan = req_matt * self.quan

                    # find the amount of material required from the lower quality supplier using formula below
                    lsupp_quan = (target_total_qual - hsupp_qual * matt_quan) / (lsupp_qual - hsupp_qual)

                    df_rel_low = self.df_supp[self.df_supp['Name'] == lsupp[0]]
                    supp_low_score = df_rel_low['Reliability'].iloc[0]
                    if supp_low_score == 'Low':
                        lsupp_quan_adj = (lsupp_quan * 0.6 // 25) * 25
                    elif supp_low_score == 'Medium':
                        lsupp_quan_adj = (lsupp_quan * 0.8 // 25) * 25
                    else:
                        lsupp_quan_adj = (lsupp_quan // 25) * 25

                    hsupp_quan = matt_quan - lsupp_quan_adj

                    if lsupp_quan_adj < lsupp_minqty:
                        lsupp_gap = lsupp_minqty - lsupp_quan_adj
                        lsupp_qgap = lsupp_gap * lsupp_qual
                        hsupp_quan += ((lsupp_qgap / hsupp_qual) // 25) * 25
                        lsupp_quan_adj = lsupp_minqty

                    if hsupp_quan < hsupp_minqty:
                        hsupp_quan = hsupp_minqty

                    lsupp_div25 = round(lsupp_quan_adj // 25)
                    for i in range(lsupp_div25):
                        hsupp_quan_new = hsupp_quan + i * 25
                        lsupp_quan_new = lsupp_quan_adj - i * 25

                        if i + 1 == lsupp_div25:
                            hsupp_quan_new = matt_quan
                            lsupp_quan_new = 0

                        if lsupp_quan_new < lsupp_minqty and lsupp_quan_new != 0:
                            pass

                        else:
                            lsupp_num_wkdl = math.ceil(lsupp_quan_new / lsupp_maxqty)
                            hsupp_num_wkdl = math.ceil(hsupp_quan_new / hsupp_maxqty)

                            lsupp_total_lead = lsupp_lead + lsupp_num_wkdl - 1
                            hsupp_total_lead = hsupp_lead + hsupp_num_wkdl - 1

                            if lsupp_quan_new == 0:
                                total_lead = hsupp_total_lead
                            elif lsupp_total_lead > hsupp_total_lead:
                                total_lead = lsupp_total_lead
                            else:
                                total_lead = hsupp_total_lead

                            lsupp_wkdldisc_rate = self.df_supp[self.df_supp['Name'] == lsupp[0]]['DIS_WKDL'].iloc[0]
                            hsupp_wkdldisc_rate = self.df_supp[self.df_supp['Name'] == hsupp[0]]['DIS_WKDL'].iloc[0]

                            lsupp_wkdl_disc = 0
                            if type(lsupp_wkdldisc_rate) != float:
                                lsupp_disc_weeks = int(lsupp_wkdldisc_rate.split('/')[1])

                                if lsupp_num_wkdl >= lsupp_disc_weeks:
                                    lsupp_wkdl_disc = int(lsupp_wkdldisc_rate.split('/')[0])

                            hsupp_wkdl_disc = 0
                            if type(hsupp_wkdldisc_rate) != float:
                                hsupp_disc_weeks = int(hsupp_wkdldisc_rate.split('/')[1])

                                if hsupp_num_wkdl >= hsupp_disc_weeks:
                                    hsupp_wkdl_disc = int(hsupp_wkdldisc_rate.split('/')[0])

                            lsupp_qtydisc_rate = self.df_supp[self.df_supp['Name'] == lsupp[0]]['DIS_QTY'].iloc[0]
                            hsupp_qtydisc_rate = self.df_supp[self.df_supp['Name'] == hsupp[0]]['DIS_QTY'].iloc[0]

                            lsupp_disc_perc = 0
                            if type(lsupp_qtydisc_rate) != float:
                                lsupp_disc_quan = int(lsupp_qtydisc_rate.split('/')[1])

                                if lsupp_disc_quan <= lsupp_quan_new:
                                    lsupp_disc_perc = int(lsupp_qtydisc_rate.split('/')[0])

                            hsupp_disc_perc = 0
                            if type(hsupp_qtydisc_rate) != float:
                                hsupp_disc_quan = int(hsupp_qtydisc_rate.split('/')[1])

                                if hsupp_disc_quan <= hsupp_quan_new:
                                    hsupp_disc_perc = int(hsupp_qtydisc_rate.split('/')[0])

                            lsupp_total_disc = lsupp_wkdl_disc + lsupp_disc_perc
                            hsupp_total_disc = hsupp_wkdl_disc + hsupp_disc_perc

                            lsupp_price_disc = lsupp_price * (100 - lsupp_total_disc) / 100
                            hsupp_price_disc = hsupp_price * (100 - hsupp_total_disc) / 100

                            total_price = round(lsupp_price_disc * lsupp_quan_new +
                                                hsupp_price_disc * hsupp_quan_new, 2)

                            if lsupp_quan_new == 0:
                                supp_dict = {'Supplier 1': [hsupp[0]],
                                             'Supplier 1 Quantity': [hsupp_quan_new],
                                             'Supplier 1 Num of Orders': [hsupp_num_wkdl],
                                             'Supplier 2': [0],
                                             'Supplier 2 Quantity': [lsupp_quan_new],
                                             'Supplier 2 Num of Orders': [lsupp_num_wkdl],
                                             'Total Price': [total_price],
                                             'Total Lead Time': [total_lead]}
                                supp_df = pd.DataFrame(supp_dict)
                                df_costs = pd.concat([df_costs, supp_df])

                            else:
                                supp_dict = {'Supplier 1': [hsupp[0]],
                                             'Supplier 1 Quantity': [hsupp_quan_new],
                                             'Supplier 1 Num of Orders': [hsupp_num_wkdl],
                                             'Supplier 2': [lsupp[0]],
                                             'Supplier 2 Quantity': [lsupp_quan_new],
                                             'Supplier 2 Num of Orders': [lsupp_num_wkdl],
                                             'Total Price': [total_price],
                                             'Total Lead Time': [total_lead]}
                                supp_df = pd.DataFrame(supp_dict)
                                df_costs = pd.concat([df_costs, supp_df])

        return df_costs

    def find_ship_info(self):
        """ calculate the total weight of a shipment and costs based on different delivery times

        Returns:
            ship_list (list): list containing total weight of shipment and cost of shipping of different delivery times
        """
        prod_weight = float(self.df_item['Weight'].iloc[0])
        total_weight = prod_weight * self.quan

        if total_weight < 100:
            pack_size = 'Small'

        elif total_weight < 250:
            pack_size = 'Large'

        else:
            pack_size = 'Freight'

        ship_list = list()
        for i in range(3):
            df_size_rows = self.df_ship[self.df_ship['Package Size'] == pack_size]
            df_time_row = df_size_rows[df_size_rows['Shipping Time'] == i]

            ship_fixed = int(df_time_row['Intercept'].iloc[0])
            ship_rate = float(df_time_row['Rate'].iloc[0])

            total_ship_cost = ship_fixed + ship_rate * total_weight
            ship_list.append([total_weight, total_ship_cost])

        return ship_list

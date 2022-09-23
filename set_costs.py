import csv
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, TypedDict
import time
from pprint import pp 


start = time.time()

prices_file = 'prices_full.csv'
cdr_file = 'cdr.csv'
out_cdr_file = cdr_file.rsplit(".")[0] + "_out.csv"

# data structure types
@dataclass
class PriceData():
    price: float
    mc: float | int
    ci: float | int

class CallRow(TypedDict):
    call_date: str
    uniqueid: float
    called_number: int
    sip_acc: str
    duration: int
    billed: int
    status: str
    instanse: str


def get_prices(prices_filepath: str) -> dict[str, PriceData]:
    with open(prices_filepath, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        return {row['code']: PriceData(price=float(row['price']), mc=int(row['mc']), ci=int(row['ci'])) for row in reader}

def pd_read_csv(filename: str) -> List[CallRow]:
    return [call for chunk in pd.read_csv(filename, delimiter=";", chunksize=5000) for call in chunk.to_dict('records')]

def get_price_for_number(number: str, prices: Dict[str, PriceData]) -> PriceData:
    if number in prices.keys():
        return PriceData(price=prices[number].price, mc=prices[number].mc, ci=prices[number].ci) 
    else:
        return get_price_for_number(number[:-1], prices)

def write_to_csv(cdr_to_csv: list[dict[str, str | int]], output_filename: str) -> None:
    header = cdr_to_csv[0].keys()
    with open(output_filename, 'w', newline='') as out_file:
        dict_writer = csv.DictWriter(out_file, header)
        dict_writer.writeheader()
        dict_writer.writerows(cdr_to_csv)
    
def calc_call_cost(price_data: PriceData, duration: int) -> float:
    price, mc, ci = price_data.price, price_data.mc, price_data.ci
    mc = 0 if duration % mc == 0 else mc
    billing_duration = mc + (duration // ci) * ci
    return round((billing_duration / 60) * price, 5)


def main() -> None:
    prices = get_prices(prices_file)
    cdr = pd_read_csv(cdr_file)
    out_cdr = []
    total_sum = 0

    for call in cdr:
        out_cdr.append(call)
        try:
            price_data = get_price_for_number(str(call['called_number']), prices)
        except RecursionError: # RecursionError can happend if there is no price for given number
            out_cdr[-1]['call_cost'] = 0
            out_cdr[-1]['call_price'] = 0
            continue
        if call['billed'] == 0:
            out_cdr[-1]['call_price'] = price_data.price
            out_cdr[-1]['call_cost'] = 0
            continue
        call_cost = calc_call_cost(price_data, call['billed'])
        total_sum += call_cost
        out_cdr[-1]['call_price'] = price_data.price
        out_cdr[-1]['call_cost'] = call_cost

    
    write_to_csv(out_cdr, out_cdr_file)
    print(f'# Total sum: {round(total_sum, 2)}')


if __name__ == "__main__":
    main()

end = time.time()
print('==============================')
print(f'# Elapsed time: {end-start}')
print('==============================')

# cdr_1.csv Total sum: 105818.22
# cdr_2.csv Total sum: 111094.31
# Total cost full :  216 912,53
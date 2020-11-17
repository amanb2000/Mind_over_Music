import asyncio
from lib.cortex import Cortex
import time
import signal_lib as signal_lib
import json


async def make_connection(cortex):
    """
    Function that authenticates with and connects to the Cortex API to get data directly 
    from the EEG headset.

    Configurable to receive raw eeg signals, band powers, accelerometer, or gyrocscope data.

    Further documentation available: https://emotiv.gitbook.io/cortex-api/
    """

    # await cortex.inspectApi()
    print("** USER LOGIN **")
    await cortex.get_user_login()
    print("** GET CORTEX INFO **")
    await cortex.get_cortex_info()
    print("** HAS ACCESS RIGHT **")
    await cortex.has_access_right()
    print("** REQUEST ACCESS **")
    await cortex.request_access()
    print("** AUTHORIZE **")
    await cortex.authorize()
    print("** GET LICENSE INFO **")
    # await cortex.get_license_info()
    print("** QUERY HEADSETS **")
    await cortex.query_headsets()
    if len(cortex.headsets) > 0:
        print("** CREATE SESSION **")
        await cortex.create_session(activate=True,
                                    headset_id=cortex.headsets[0])
        # print("** CREATE RECORD **")
        # await cortex.create_record(title="test record 1")
        print("\n\n** SUBSCRIBE EEG **\n\n")
        # await cortex.subscribe(['eeg']) # Subscribing to the FFT band powers (for each electrode: alpha, low beta, high beta, gamma, and theta)
        await cortex.subscribe(['pow'])
        # while cortex.packet_count < 10:
        while True:
            dat = await cortex.get_data()
            signal_lib.eeg_to_file(dat)

        await cortex.close_session()



last_time = 0
this_time = time.time()



def main():
    cortex = Cortex('./cortex_creds')
    asyncio.run(make_connection(cortex))
    cortex.close()

if __name__ == '__main__':
    main()



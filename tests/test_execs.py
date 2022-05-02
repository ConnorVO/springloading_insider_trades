from datetime import datetime
import logging
import pytest
from settings import SUPABASE, SUPABASE_EXECS_TABLE, SUPABASE_FILINGS_TABLE
from springloading_insider_trades.db.db import (
    _update_exec_data,
    delete_exec,
    insert_filing_data,
)
from springloading_insider_trades.sec_api.classes.Company import Company
from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing
from springloading_insider_trades.sec_api.classes.Transaction import Transaction

logger = logging.getLogger(__name__)

OWNER_CIK = 1


class TestExecs:
    """This is mostly testing pricing updates"""

    def _helper(self, open_price, ninety_day_price):
        data = {
            "owner_cik": OWNER_CIK,
            "stock_prices": {"open": open_price, "90_day": ninety_day_price},
        }
        exec_update_res = _update_exec_data(data)
        logger.info(exec_update_res)
        return exec_update_res

    def _delete_exec(self, owner_cik):
        delete_exec(owner_cik)

    def test_new_no_ninety(self):
        OPEN_PRICE = 100
        NINETY_DAY_PRICE = None
        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": None,
                    "num_trades": None,
                    "num_correct": None,
                }
            )
            .execute()
        )
        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert (
            exec_update_res == None
        ), "Res should be None if there is nothing to update"

        self._delete_exec(OWNER_CIK)

    def test_new_no_open(self):
        OPEN_PRICE = None
        NINETY_DAY_PRICE = 90
        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": None,
                    "num_trades": None,
                    "num_correct": None,
                }
            )
            .execute()
        )
        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert (
            exec_update_res == None
        ), "Res should be None if there is nothing to update"

        self._delete_exec(OWNER_CIK)

    def test_new_no_open_and_no_ninety(self):
        OPEN_PRICE = None
        NINETY_DAY_PRICE = None
        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": None,
                    "num_trades": None,
                    "num_correct": None,
                }
            )
            .execute()
        )

        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert (
            exec_update_res == None
        ), "Res should be None if there is nothing to update"

        self._delete_exec(OWNER_CIK)

    def test_new_pos_data(self):
        OPEN_PRICE = 100
        NINETY_DAY_PRICE = 110
        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": None,
                    "num_trades": None,
                    "num_correct": None,
                }
            )
            .execute()
        )
        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert exec_update_res.data[0]["num_trades"] == 1, "Num Trades Didn't Update"
        assert (
            exec_update_res.data[0]["num_correct"] == 1
        ), "Num Correct Didn't Update Properly"
        assert exec_update_res.data[0]["ninety_day_return"] == pytest.approx(
            NINETY_DAY_PRICE / OPEN_PRICE - 1, 0.001
        ), "90 Day Return Didn't Update Properly"

        self._delete_exec(OWNER_CIK)

    def test_new_neg_data(self):
        OPEN_PRICE = 100
        NINETY_DAY_PRICE = 90
        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": None,
                    "num_trades": None,
                    "num_correct": None,
                }
            )
            .execute()
        )
        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert exec_update_res.data[0]["num_trades"] == 1, "Num Trades Didn't Update"
        assert (
            exec_update_res.data[0]["num_correct"] == 0
        ), "Num Correct Didn't Update Properly"
        assert exec_update_res.data[0]["ninety_day_return"] == pytest.approx(
            NINETY_DAY_PRICE / OPEN_PRICE - 1, 0.001
        ), "90 Day Rerturn Didn't Update Properly"

        self._delete_exec(OWNER_CIK)

        # new_filing = Form4Filing(
        #     Company(1, "Test Co", "testco"),
        #     datetime.now(),
        #     "connor",
        #     1,
        #     False,
        #     True,
        #     False,
        #     False,
        #     "ceo",
        #     Transaction(
        #         datetime.now(), "Common Stock", "A", 100, 10, 110, "A", "D", [], 1
        #     ),
        #     [],
        #     [],
        #     "google.com",
        # )
        # insert_filing_data(new_filing)
        # data = {
        #     "owner_cik": 1,
        #     "filing_id": new_filing.id,
        #     "stock_prices": {"open": 10, "90_day": 11},
        # }
        # _update_exec_data(data)

    def test_adding_one_pos_to_pos(self):
        OPEN_PRICE = 100
        NINETY_DAY_PRICE = 110
        NINETY_DAY_RETURN = 0.2
        NUM_TRADES = 1
        NUM_CORRECT = 1

        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": NINETY_DAY_RETURN,
                    "num_trades": NUM_TRADES,
                    "num_correct": NUM_CORRECT,
                }
            )
            .execute()
        )
        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert (
            exec_update_res.data[0]["num_trades"] == NUM_TRADES + 1
        ), "Num Trades Didn't Update"
        assert (
            exec_update_res.data[0]["num_correct"] == NUM_CORRECT + 1
        ), "Num Correct Didn't Update Properly"
        assert exec_update_res.data[0]["ninety_day_return"] == pytest.approx(
            (NINETY_DAY_RETURN * NUM_TRADES + (NINETY_DAY_PRICE / OPEN_PRICE - 1))
            / (NUM_TRADES + 1),
            0.001,
        ), "90 Day Return Didn't Update Properly"

        self._delete_exec(OWNER_CIK)

    def test_adding_one_neg(self):
        OPEN_PRICE = 100
        NINETY_DAY_PRICE = 90
        NINETY_DAY_RETURN = -0.1
        NUM_TRADES = 1
        NUM_CORRECT = 0

        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": NINETY_DAY_RETURN,
                    "num_trades": NUM_TRADES,
                    "num_correct": NUM_CORRECT,
                }
            )
            .execute()
        )
        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert (
            exec_update_res.data[0]["num_trades"] == NUM_TRADES + 1
        ), "Num Trades Didn't Update"
        assert (
            exec_update_res.data[0]["num_correct"] == NUM_CORRECT
        ), "Num Correct Didn't Update Properly"
        assert exec_update_res.data[0]["ninety_day_return"] == pytest.approx(
            (NINETY_DAY_RETURN * NUM_TRADES + (NINETY_DAY_PRICE / OPEN_PRICE - 1))
            / (NUM_TRADES + 1),
            0.001,
        ), "90 Day Return Didn't Update Properly"

        self._delete_exec(OWNER_CIK)

    def test_adding_multi_pos(self):
        OPEN_PRICE = 100
        NINETY_DAY_PRICE = 110
        NINETY_DAY_RETURN = 0.2
        NUM_TRADES = 3
        NUM_CORRECT = 3

        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": NINETY_DAY_RETURN,
                    "num_trades": NUM_TRADES,
                    "num_correct": NUM_CORRECT,
                }
            )
            .execute()
        )
        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert (
            exec_update_res.data[0]["num_trades"] == NUM_TRADES + 1
        ), "Num Trades Didn't Update"
        assert (
            exec_update_res.data[0]["num_correct"] == NUM_CORRECT + 1
        ), "Num Correct Didn't Update Properly"
        assert exec_update_res.data[0]["ninety_day_return"] == pytest.approx(
            (NINETY_DAY_RETURN * NUM_TRADES + (NINETY_DAY_PRICE / OPEN_PRICE - 1))
            / (NUM_TRADES + 1),
            0.001,
        ), "90 Day Return Didn't Update Properly"

        self._delete_exec(OWNER_CIK)

    def test_adding_multi_neg(self):
        OPEN_PRICE = 100
        NINETY_DAY_PRICE = 90
        NINETY_DAY_RETURN = -0.2
        NUM_TRADES = 3
        NUM_CORRECT = 0

        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": NINETY_DAY_RETURN,
                    "num_trades": NUM_TRADES,
                    "num_correct": NUM_CORRECT,
                }
            )
            .execute()
        )
        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert (
            exec_update_res.data[0]["num_trades"] == NUM_TRADES + 1
        ), "Num Trades Didn't Update"
        assert (
            exec_update_res.data[0]["num_correct"] == NUM_CORRECT
        ), "Num Correct Didn't Update Properly"
        assert exec_update_res.data[0]["ninety_day_return"] == pytest.approx(
            (NINETY_DAY_RETURN * NUM_TRADES + (NINETY_DAY_PRICE / OPEN_PRICE - 1))
            / (NUM_TRADES + 1),
            0.001,
        ), "90 Day Return Didn't Update Properly"

        self._delete_exec(OWNER_CIK)

    def test_passing_multi_mix(self):
        OPEN_PRICE = 100
        NINETY_DAY_PRICE = 110
        NINETY_DAY_RETURN = 0
        NUM_TRADES = 3
        NUM_CORRECT = 1

        execs_res = (
            (SUPABASE.table(SUPABASE_EXECS_TABLE))
            .upsert(
                {
                    "cik": OWNER_CIK,
                    "name": "connor",
                    "ninety_day_return": NINETY_DAY_RETURN,
                    "num_trades": NUM_TRADES,
                    "num_correct": NUM_CORRECT,
                }
            )
            .execute()
        )
        exec_update_res = self._helper(OPEN_PRICE, NINETY_DAY_PRICE)

        assert (
            exec_update_res.data[0]["num_trades"] == NUM_TRADES + 1
        ), "Num Trades Didn't Update"
        assert (
            exec_update_res.data[0]["num_correct"] == NUM_CORRECT + 1
        ), "Num Correct Didn't Update Properly"
        assert exec_update_res.data[0]["ninety_day_return"] == pytest.approx(
            (NINETY_DAY_RETURN * NUM_TRADES + (NINETY_DAY_PRICE / OPEN_PRICE - 1))
            / (NUM_TRADES + 1),
            0.001,
        ), "90 Day Return Didn't Update Properly"

        self._delete_exec(OWNER_CIK)

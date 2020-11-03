"""
Principal Author: Eric Linden
Description :

Notes :
November 03, 2020
"""

import unittest


class TestNetworkHealthApp(unittest.TestCase):
    def test_callback_func(self):
        import json
        from app import callback_func

        # Should add new results to pings and pass_fail in the store
        response = json.loads(callback_func(
            tick=1,
            store_state=dict(pings=[1, 2, 3], pass_fail='1'),
            outputs_list=[
                {'id': 'ping-output', 'property': 'children'},
                {'id': 'store', 'property': 'data'}],
        ))

        self.assertTrue(len(response['response']), 2)
        self.assertEqual(len(response['response']['store']['data']['pings']), 4)
        self.assertEqual(len(response['response']['store']['data']['pass_fail']), 2)

        # Should reset the pings back to just 1, and keep the pass_fail to just 20 results
        response = json.loads(callback_func(
            tick=1,
            store_state=dict(pings=['1'] * 200, pass_fail='1' * 21),
            outputs_list=[
                {'id': 'ping-output', 'property': 'children'},
                {'id': 'store', 'property': 'data'}],
        ))

        self.assertTrue(len(response['response']), 2)
        self.assertEqual(len(response['response']['store']['data']['pings']), 1)
        self.assertEqual(len(response['response']['store']['data']['pass_fail']), 20)

    def test_update_stored_results(self):
        from app import update_stored_results

        # Should return single result if no history
        response = update_stored_results(ping_time='test', ping_result=[1, 2, 3], history=[])
        self.assertEqual(response, ['test: 1 - 2 - 3'])

        # Should combine history with new result
        response = update_stored_results(ping_time='test', ping_result=[1, 2, 3], history=['test'])
        self.assertEqual(response, ['test', 'test: 1 - 2 - 3'])

    def test_write_out_data(self):
        pass

    def test_run_speed_test(self):
        from app import run_speed_test

        response = run_speed_test()
        self.assertTrue('Download speed: ' in response)
        self.assertTrue('Upload speed: ' in response)

        speeds_str = response.replace('Download speed: ', '').replace('Upload speed: ', '')
        speeds_list = speeds_str.split(', ')
        self.assertTrue(all(isinstance(float(x), float) for x in speeds_list))


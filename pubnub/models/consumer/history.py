from pubnub import crypto as pn_crypto


class PNHistoryResult(object):
    def __init__(self, messages, start_timetoken, end_timetoken):
        self.messages = messages
        self.start_timetoken = start_timetoken
        self.end_timetoken = end_timetoken

    @classmethod
    def from_json(cls, json_input, include_tt_option=False, cipher=None):
        start_timetoken = json_input[1]
        end_timetoken = json_input[2]

        raw_items = json_input[0]
        messages = []

        for item in raw_items:
            if isinstance(item, dict) and 'timetoken' in item and 'message' in item and include_tt_option:
                message = PNHistoryItemResult(item['message'], item['timetoken'])
            else:
                message = PNHistoryItemResult(item)

            if cipher is not None:
                message.decrypt(cipher)

            messages.append(message)

        return PNHistoryResult(
            messages=messages,
            start_timetoken=start_timetoken,
            end_timetoken=end_timetoken
        )


class PNHistoryItemResult(object):
    def __init__(self, entry, timetoken=None):
        self.timetoken = timetoken
        self.entry = entry

    def decrypt(self, cipher_key):
        self.entry = pn_crypto.decrypt(cipher_key, self.entry)

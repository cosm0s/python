try: import json
except ImportError: import simplejson as json

import time
import hashlib
import uuid
import sys

class PubnubBase(object):
    def __init__(
        self,
        publish_key,
        subscribe_key,
        secret_key = False,
        cipher_key = False,
        ssl_on = False,
        origin = 'pubsub.pubnub.com',
        UUID = None
    ) :
        """
        #**
        #* Pubnub
        #*
        #* Init the Pubnub Client API
        #*
        #* @param string publish_key required key to send messages.
        #* @param string subscribe_key required key to receive messages.
        #* @param string secret_key optional key to sign messages.
        #* @param boolean ssl required for 2048 bit encrypted messages.
        #* @param string origin PUBNUB Server Origin.
        #* @param string pres_uuid optional identifier for presence (auto-generated if not supplied)
        #**

        ## Initiat Class
        pubnub = Pubnub( 'PUBLISH-KEY', 'SUBSCRIBE-KEY', 'SECRET-KEY', False )

        """
        self.origin        = origin
        self.limit         = 1800
        self.publish_key   = publish_key
        self.subscribe_key = subscribe_key
        self.secret_key    = secret_key
        self.cipher_key    = cipher_key
        self.ssl           = ssl_on


        if self.ssl :
            self.origin = 'https://' + self.origin
        else :
            self.origin = 'http://'  + self.origin
        
        self.uuid = UUID or str(uuid.uuid4())

        if type(sys.version_info) is tuple:
            self.python_version = 2
            self.pc             = PubnubCrypto2()
        else:
            self.python_version = 3
            self.pc             = PubnubCrypto3()

        
        if not isinstance(self.uuid, str):
            raise AttributeError("pres_uuid must be a string")

    def sign(self, channel, message):
        ## Sign Message
        if self.secret_key:
            signature = hashlib.md5('/'.join([
                self.publish_key,
                self.subscribe_key,
                self.secret_key,
                channel,
                message
            ])).hexdigest()
        else:
            signature = '0'
        return signature

    def encrypt(self, message):
        if self.cipher_key:
            message = json.dumps(self.pc.encrypt(self.cipher_key, json.dumps(message)).replace('\n',''))
        else :
            message = json.dumps(message)

        return message;

    def decrypt(self, message):
        if self.cipher_key:
            message = self.pc.decrypt(self.cipher_key, message)

        return message

    def _return_wrapped_callback(self, callback=None):
        def _new_format_callback(response):
            if 'payload' in response:
                if (callback != None): callback({'message' : response['message'], 'payload' : response['payload']})
            else:
                if (callback != None):callback(response)
        if (callback != None): return _new_format_callback


    def publish( self, args ) :
        """
        #**
        #* Publish
        #*
        #* Send a message to a channel.
        #*
        #* @param array args with channel and message.
        #* @return array success information.
        #**

        ## Publish Example
        info = pubnub.publish({
            'channel' : 'hello_world',
            'message' : {
                'some_text' : 'Hello my World'
            }
        })
        print(info)

        """
        ## Fail if bad input.
        if not (args['channel'] and args['message']) :
            return [ 0, 'Missing Channel or Message' ]

        ## Capture User Input
        channel = str(args['channel'])

        ## Capture Callback
        if 'callback' in args :
            callback = args['callback']
        else :
            callback = None 

        #message = json.dumps(args['message'], separators=(',',':'))
        message = self.encrypt(args['message'])

        signature = self.sign(channel, message)

        ## Send Message
        return self._request({"urlcomponents": [
            'publish',
            self.publish_key,
            self.subscribe_key,
            signature,
            channel,
            '0',
            message
        ]'urlparams' : {'auth' : self.auth_key}}, self._return_wrapped_callback(callback))
    
    def presence( self, args ) :
        """
        #**
        #* presence
        #*
        #* This is BLOCKING.
        #* Listen for presence events on a channel.
        #*
        #* @param array args with channel and callback.
        #* @return false on fail, array on success.
        #**

        ## Presence Example
        def pres_event(message) :
            print(message)
            return True

        pubnub.presence({
            'channel'  : 'hello_world',
            'callback' : receive 
        })
        """

        ## Fail if missing channel
        if not 'channel' in args :
            raise Exception('Missing Channel.')
            return False

        ## Fail if missing callback
        if not 'callback' in args :
            raise Exception('Missing Callback.')
            return False

        ## Capture User Input
        channel   = str(args['channel'])
        callback  = args['callback']
        subscribe_key = args.get('subscribe_key') or self.subscribe_key
        
        return self.subscribe({'channel': channel+'-pnpres', 'subscribe_key':subscribe_key, 'callback': self._return_wrapped_callback(callback)})
    
    
    def here_now( self, args ) :
        """
        #**
        #* Here Now
        #*
        #* Load current occupancy from a channel.
        #*
        #* @param array args with 'channel'.
        #* @return mixed false on fail, array on success.
        #*

        ## Presence Example
        here_now = pubnub.here_now({
            'channel' : 'hello_world',
        })
        print(here_now['occupancy'])
        print(here_now['uuids'])

        """
        channel = str(args['channel'])

        ## Capture Callback
        if 'callback' in args :
            callback = args['callback']
        else :
            callback = None
        
        ## Fail if bad input.
        if not channel :
            raise Exception('Missing Channel')
            return False
        
        ## Get Presence Here Now
        return self._request({"urlcomponents": [
            'v2','presence',
            'sub_key', self.subscribe_key,
            'channel', channel
        ]}, callback);
        
        
    def history( self, args ) :
        """
        #**
        #* History
        #*
        #* Load history from a channel.
        #*
        #* @param array args with 'channel' and 'limit'.
        #* @return mixed false on fail, array on success.
        #*

        ## History Example
        history = pubnub.history({
            'channel' : 'hello_world',
            'limit'   : 1
        })
        print(history)

        """
        ## Capture User Input
        limit   = 'limit' in args and int(args['limit']) or 10
        channel = str(args['channel'])

        ## Fail if bad input.
        if not channel :
            raise Exception('Missing Channel')
            return False

        ## Capture Callback
        if 'callback' in args :
            callback = args['callback']
        else :
            callback = None

        ## Get History
        return self._request({ "urlcomponents" : [
            'history',
            self.subscribe_key,
            channel,
            '0',
            str(limit)
        ] }, callback);

    def detailedHistory(self, args) :
        """
        #**
        #* Detailed History
        #*
        #* Load Detailed history from a channel.
        #*
        #* @param array args with 'channel', optional: 'start', 'end', 'reverse', 'count'
        #* @return mixed false on fail, array on success.
        #*

        ## History Example
        history = pubnub.detailedHistory({
            'channel' : 'hello_world',
            'count'   : 5
        })
        print(history)

        """
        ## Capture User Input
        channel = str(args['channel'])

        params = dict() 
        count = 100    
        
        if 'count' in args:
            count = int(args['count'])

        params['count'] = str(count)    
        
        if 'reverse' in args:
            params['reverse'] = str(args['reverse']).lower()

        if 'start' in args:
            params['start'] = str(args['start'])

        if 'end' in args:
            params['end'] = str(args['end'])

        ## Fail if bad input.
        if not channel :
            raise Exception('Missing Channel')
            return False

        ## Capture Callback
        if 'callback' in args :
            callback = args['callback']
        else :
            callback = None 

        ## Get History
        return self._request({ 'urlcomponents' : [
            'v2',
            'history',
            'sub-key',
            self.subscribe_key,
            'channel',
            channel,
        ],'urlparams' : params }, callback=callback);

    def time(self, args = None) :
        """
        #**
        #* Time
        #*
        #* Timestamp from PubNub Cloud.
        #*
        #* @return int timestamp.
        #*

        ## PubNub Server Time Example
        timestamp = pubnub.time()
        print(timestamp)

        """
        ## Capture Callback
        if args and 'callback' in args :
            callback = args['callback']
        else :
            callback = None 
        time = self._request({'urlcomponents' : [
            'time',
            '0'
        ]}, callback)
        if time != None:
            return time[0]


    def _encode( self, request ) :
        return [
            "".join([ ' ~`!@#$%^&*()+=[]\\{}|;\':",./<>?'.find(ch) > -1 and
                hex(ord(ch)).replace( '0x', '%' ).upper() or
                ch for ch in list(bit)
            ]) for bit in request]
    
    def getUrl(self,request):
        ## Build URL
        url = self.origin + '/' + "/".join([
            "".join([ ' ~`!@#$%^&*()+=[]\\{}|;\':",./<>?'.find(ch) > -1 and
                hex(ord(ch)).replace( '0x', '%' ).upper() or
                ch for ch in list(bit)
            ]) for bit in request["urlcomponents"]])
        if ("urlparams" in request):
            url = url + '?' + "&".join([ x + "=" + y  for x,y in request["urlparams"].items()])
        return url

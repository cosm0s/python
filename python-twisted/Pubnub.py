## www.pubnub.com - PubNub Real-time push service in the cloud. 
# coding=utf8

## PubNub Real-time Push APIs and Notifications Framework
## Copyright (c) 2010 Stephen Blum
## http://www.pubnub.com/

## -----------------------------------
## PubNub 3.3.5 Real-time Push Cloud API
## -----------------------------------


from Crypto.Cipher import AES
from Crypto.Hash import MD5
from base64 import encodestring, decodestring 
import hashlib
import hmac

class PubnubCrypto2() :
    """
    #**
    #* PubnubCrypto
    #*
    #**

    ## Initiate Class
    pc = PubnubCrypto

    """
   
    def pad( self, msg, block_size=16 ):
        """
        #**
        #* pad
        #*
        #* pad the text to be encrypted
        #* appends a padding character to the end of the String
        #* until the string has block_size length
        #* @return msg with padding.
        #**
        """
        padding = block_size - (len(msg) % block_size)
        return msg + chr(padding)*padding
       
    def depad( self, msg ):
        """
        #**
        #* depad
        #*
        #* depad the decryptet message"
        #* @return msg without padding.
        #**
        """
        return msg[0:-ord(msg[-1])]

    def getSecret( self, key ):
        """
        #**
        #* getSecret
        #*
        #* hases the key to MD5
        #* @return key in MD5 format
        #**
        """
        return hashlib.sha256(key).hexdigest()

    def encrypt( self, key, msg ):
        """
        #**
        #* encrypt
        #*
        #* encrypts the message
        #* @return message in encrypted format
        #**
        """
        secret = self.getSecret(key)
        Initial16bytes='0123456789012345'
        cipher = AES.new(secret[0:32],AES.MODE_CBC,Initial16bytes)
        enc = encodestring(cipher.encrypt(self.pad(msg)))
        return enc
    def decrypt( self, key, msg ):
        """
        #**
        #* decrypt
        #*
        #* decrypts the message
        #* @return message in decryped format
        #**
        """
        secret = self.getSecret(key)
        Initial16bytes='0123456789012345'
        cipher = AES.new(secret[0:32],AES.MODE_CBC,Initial16bytes)
        return self.depad((cipher.decrypt(decodestring(msg))))


class PubnubCrypto3() :
    """
    #**
    #* PubnubCrypto
    #*
    #**

    ## Initiate Class
    pc = PubnubCrypto

    """
   
    def pad( self, msg, block_size=16 ):
        """
        #**
        #* pad
        #*
        #* pad the text to be encrypted
        #* appends a padding character to the end of the String
        #* until the string has block_size length
        #* @return msg with padding.
        #**
        """
        padding = block_size - (len(msg) % block_size)
        return msg + (chr(padding)*padding).encode('utf-8')
       
    def depad( self, msg ):
        """
        #**
        #* depad
        #*
        #* depad the decryptet message"
        #* @return msg without padding.
        #**
        """
        return msg[0:-ord(msg[-1])]

    def getSecret( self, key ):
        """
        #**
        #* getSecret
        #*
        #* hases the key to MD5
        #* @return key in MD5 format
        #**
        """
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def encrypt( self, key, msg ):
        """
        #**
        #* encrypt
        #*
        #* encrypts the message
        #* @return message in encrypted format
        #**
        """
        secret = self.getSecret(key)
        Initial16bytes='0123456789012345'
        cipher = AES.new(secret[0:32],AES.MODE_CBC,Initial16bytes)
        return encodestring(cipher.encrypt(self.pad(msg.encode('utf-8')))).decode('utf-8')
    def decrypt( self, key, msg ):
        """
        #**
        #* decrypt
        #*
        #* decrypts the message
        #* @return message in decryped format
        #**
        """
        secret = self.getSecret(key)
        Initial16bytes='0123456789012345'
        cipher = AES.new(secret[0:32],AES.MODE_CBC,Initial16bytes)
        return (cipher.decrypt(decodestring(msg.encode('utf-8')))).decode('utf-8')


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


try:
    from hashlib import sha256
    digestmod = sha256
except ImportError:
    import Crypto.Hash.SHA256 as digestmod
    sha256 = digestmod.new
import hmac

class PubnubCoreAsync(PubnubBase):

    def start(self): pass 
    def stop(self):  pass

    def __init__(
        self,
        publish_key,
        subscribe_key,
        secret_key = False,
        cipher_key = False,
        ssl_on = False,
        origin = 'pubsub.pubnub.com',
        uuid = None
    ) :
        """
        #**
        #* Pubnub
        #*
        #* Init the Pubnub Client API
        #*
        #* @param string publish_key required key to send messages.
        #* @param string subscribe_key required key to receive messages.
        #* @param string secret_key required key to sign messages.
        #* @param boolean ssl required for 2048 bit encrypted messages.
        #* @param string origin PUBNUB Server Origin.
        #**

        ## Initiat Class
        pubnub = Pubnub( 'PUBLISH-KEY', 'SUBSCRIBE-KEY', 'SECRET-KEY', False )

        """
        super(PubnubCoreAsync, self).__init__(
            publish_key=publish_key,
            subscribe_key=subscribe_key,
            secret_key=secret_key,
            cipher_key=cipher_key,
            ssl_on=ssl_on,
            origin=origin,
            UUID=uuid
        )        

        self.subscriptions = {}
        self.timetoken     = 0
        self.version       = '3.3.4'
        self.accept_encoding = 'gzip'
        self.SUB_RECEIVER  = None
        self._connect    = None

    def get_channel_list(self, channels):
        channel = ''
        first = True
        for ch in channels:
            if not channels[ch]['subscribed']:
                continue
            if not first:
                channel += ','
            else:
                first = False
            channel += ch
        return channel

    def subscribe( self, args=None, sync=False ) :
        """
        #**
        #* Subscribe
        #*
        #* This is NON-BLOCKING.
        #* Listen for a message on a channel.
        #*
        #* @param array args with channel and message.
        #* @return false on fail, array on success.
        #**

        ## Subscribe Example
        def receive(message) :
            print(message)
            return True

        ## On Connect Callback
        def connected() :
            pubnub.publish({
                'channel' : 'hello_world',
                'message' : { 'some_var' : 'text' }
            })

        ## Subscribe
        pubnub.subscribe({
            'channel'  : 'hello_world',
            'connect'  : connected,
            'callback' : receive
        })

        """

        if sync is True and self.susbcribe_sync is not None:
            self.susbcribe_sync(args)
            return

        def _invoke(func,msg=None):
            if func is not None:
                if msg is not None:
                    func(msg)
                else:
                    func()

        def _invoke_connect():
            for ch in self.subscriptions:
                chobj = self.subscriptions[ch]
                if chobj['connected'] is False:
                    chobj['connected'] = True
                    _invoke(chobj['connect'])

        def _invoke_error(err=None):
            for ch in self.subscriptions:
                chobj = self.subscriptions[ch]
                _invoke(chobj.error,err)


        if callback is None:
            _invoke(error, "Callback Missing")
            return

        if channel is None:
            _invoke(error, "Channel Missing")
            return

        def _get_channel():
            for ch in self.subscriptions:
                chobj = self.subscriptions[ch]
                if chobj['subscribed'] is True:
                    return chobj


        ## New Channel?
        if not channel in self.subscriptions:
            self.subscriptions[channel] = {
                'name'          : channel,
                'first'         : False,
                'connected'     : False,
                'subscribed'    : True,
                'callback'      : callback,
                'connect'       : connect,
                'disconnect'    : disconnect,
                'reconnect'     : reconnect
            }

        ## return if already connected to channel
        if self.subscriptions[channel]['connected'] :
            _invoke(error, "Already Connected")
            return
            

        ## SUBSCRIPTION RECURSION 
        def _connect():
          
            self._reset_offline()

            def sub_callback(response):
                print response
                ## ERROR ?
                if not response or error in response:
                    _invoke_error()

                _invoke_connect()


                self.timetoken = response[1]

                if len(response) > 2:
                    channel_list = response[2].split(',')
                    response_list = response[0]
                    for ch in enumerate(channel_list):
                        if ch[1] in self.subscriptions:
                            chobj = self.subscriptions[ch[1]]
                            _invoke(chobj['callback'],self.decrypt(response_list[ch[0]]))
                else:
                    response_list = response[0]
                    chobj = _get_channel()
                    for r in response_list:
                        if chobj:
                            _invoke(chobj['callback'], self.decrypt(r))


                _connect()



            channel_list = self.get_channel_list(self.subscriptions)
            print channel_list
            ## CONNECT TO PUBNUB SUBSCRIBE SERVERS
            try:
                self.SUB_RECEIVER = self._request( { "urlcomponents" : [
                    'subscribe',
                    self.subscribe_key,
                    channel_list,
                    '0',
                    str(self.timetoken)
                ], "urlparams" : {"uuid":self.uuid} }, sub_callback, single=True )
            except Exception as e:
                self.timeout( 1, _connect)
                return

        self._connect = _connect


        ## BEGIN SUBSCRIPTION (LISTEN FOR MESSAGES)
        _connect()

    def _reset_offline(self):
        if self.SUB_RECEIVER is not None:
            self.SUB_RECEIVER()
        self.SUB_RECEIVER = None

    def CONNECT(self):
        self._reset_offline()
        self._connect()


    def unsubscribe( self, args ):
        #print(args['channel'])
        channel = str(args['channel'])
        if not (channel in self.subscriptions):
            return False

        ## DISCONNECT
        self.subscriptions[channel]['connected'] = 0
        self.subscriptions[channel]['subscribed'] = False
        self.subscriptions[channel]['timetoken'] = 0
        self.subscriptions[channel]['first']     = False
        self.CONNECT()


from twisted.web.client import getPage
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, ContentDecoderAgent, RedirectAgent, GzipDecoder
from twisted.web.client import HTTPConnectionPool
from twisted.web.http_headers import Headers
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.task import LoopingCall
import twisted
from hashlib import sha256
import time

pnconn_pool = HTTPConnectionPool(reactor, persistent=True)
pnconn_pool.maxPersistentPerHost    = 100000
pnconn_pool.cachedConnectionTimeout = 310
pnconn_pool.retryAutomatically = True

class Pubnub(PubnubCoreAsync):

    def start(self): reactor.run()
    def stop(self):  reactor.stop()
    def timeout( self, delay, callback ):
        reactor.callLater( delay, callback )

    def __init__(
        self,
        publish_key,
        subscribe_key,
        secret_key = False,
        cipher_key = False,
        ssl_on = False,
        origin = 'pubsub.pubnub.com'
    ) :
        super(Pubnub, self).__init__(
            publish_key=publish_key,
            subscribe_key=subscribe_key,
            secret_key=secret_key,
            cipher_key=cipher_key,
            ssl_on=ssl_on,
            origin=origin,
        )        
        self.headers = {}
        self.headers['User-Agent'] = ['Python-Twisted']
        #self.headers['Accept-Encoding'] = [self.accept_encoding]
        self.headers['V'] = [self.version]

    def _request( self, request, callback, single=False ) :
        global pnconn_pool

        ## Build URL
        '''
        url = self.origin + '/' + "/".join([
            "".join([ ' ~`!@#$%^&*()+=[]\\{}|;\':",./<>?'.find(ch) > -1 and
                hex(ord(ch)).replace( '0x', '%' ).upper() or
                ch for ch in list(bit)
            ]) for bit in request])
        '''
        url = self.getUrl(request)

        agent       = ContentDecoderAgent(RedirectAgent(Agent(
            reactor,
            contextFactory = WebClientContextFactory(),
            pool = self.ssl and None or pnconn_pool
        )), [('gzip', GzipDecoder)])

        request     = agent.request( 'GET', url, Headers(self.headers), None )

        if single is True:
            id = time.time()
            self.id = id

        def received(response):
            finished = Deferred()
            response.deliverBody(PubNubResponse(finished))
            return finished

        def complete(data):
            if single is True:
                if not id == self.id:
                    return None
            try:
                callback(eval(data))
            except Exception as e:
                pass
                #need error handling here

        def abort():
            pass

        request.addCallback(received)
        request.addBoth(complete)

        return abort

class WebClientContextFactory(ClientContextFactory):
    def getContext(self, hostname, port):
        return ClientContextFactory.getContext(self)
	   
class PubNubResponse(Protocol):
    def __init__( self, finished ):
        self.finished = finished

    def dataReceived( self, bytes ):
            self.finished.callback(bytes)


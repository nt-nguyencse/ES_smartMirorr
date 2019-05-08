/ccđmk#from websocket import create_connection
#ws = create_connection("ws://echo.websocket.org/")
#print("Sending 'Hello, World'...mmmmmmmmmmmm")
#ws.send("Hello, World......hmmmmmmmmmmm")
#print("Sent")
#print("Receiving...")
#result =  ws.recv()
#print("Received '%s'" % result)
#ws.close()
##################
import json
from os.path import join, dirname
from watson_developer_cloud import SpeechToTextV1

speech_to_text = SpeechToTextV1(
    username='conloctheki1998@gmail.com',
    password='2018@Kstn',
    x_watson_learning_opt_out=True
)

print(json.dumps(speech_to_text.models(), indent=2))
aqqxs\
print(json.dumps(speech_to_text.get_model('en-US_BroadbandModel'), indent=2))

with open(join(dirname(__file__), '../genevieve.wav'),'rb') as audio_file:
    data = json.dumps(speech_to_text.recognize(audio_file, content_type='audio/wav', timestamps=False, word_confidence=False, continuous=True), indent=2)
    print(data)
#########################
#API IBM Watson: cLR5aTlONiYrcGTq_On_5n3oDBh9Kw79sZQ42aFowOjz
#https://gateway-wdc.watsonplatform.net/speech-to-text/api
#
# Copyright IBM Corp. 2014
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Author: Daniel Bolanos
# Date:   2015

# coding=utf-8

import json                        # json
import threading                   # multi threading
import os                          # for listing directories
import queue as Queue              # queue used for thread syncronization
import sys                         # system calls
import argparse                    # for parsing arguments
import base64                      # necessary to encode in base64
#                                  # according to the RFC2045 standard
import requests                    # python HTTP requests library

# WebSockets
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory, connectWS
from twisted.python import log
from twisted.internet import ssl, reactor

try:
    raw_input          # Python 2
except NameError:
    raw_input = input  # Python 3


class Utils:

    @staticmethod
    def getAuthenticationToken(hostname, serviceName, username, password):

        fmt = hostname + "{0}/authorization/api/v1/token?url={0}/{1}/api"
        uri = fmt.format(hostname, serviceName)
        uri = uri.replace("wss://", "https://").replace("ws://", "https://")
        print(uri)
        auth = (username, password)
        headers = {'Accept': 'application/json'}
        resp = requests.get(uri, auth=auth, verify=False, headers=headers,
                            timeout=(30, 30))
        print(resp.text)
        jsonObject = resp.json()
        return jsonObject['token']


class WSInterfaceFactory(WebSocketClientFactory):

    def __init__(self, queue, summary, dirOutput, contentType, model,
                 url=None, headers=None, debug=None):

        WebSocketClientFactory.__init__(self, url=url, headers=headers)
        self.queue = queue
        self.summary = summary
        self.dirOutput = dirOutput
        self.contentType = contentType
        self.model = model
        self.queueProto = Queue.Queue()

        self.openHandshakeTimeout = 10
        self.closeHandshakeTimeout = 10

        # start the thread that takes care of ending the reactor so
        # the script can finish automatically (without ctrl+c)
        endingThread = threading.Thread(target=self.endReactor, args=())
        endingThread.daemon = True
        endingThread.start()

    def prepareUtterance(self):

        try:
            utt = self.queue.get_nowait()
            self.queueProto.put(utt)
            return True
        except Queue.Empty:
            print("getUtterance: no more utterances to process, queue is "
                  "empty!")
            return False

    def endReactor(self):

        self.queue.join()
        print("about to stop the reactor!")
        reactor.stop()

    # this function gets called every time connectWS is called (once
    # per WebSocket connection/session)
    def buildProtocol(self, addr):

        try:
            utt = self.queueProto.get_nowait()
            proto = WSInterfaceProtocol(self, self.queue, self.summary,
                                        self.dirOutput, self.contentType)
            proto.setUtterance(utt)
            return proto
        except Queue.Empty:
            print("queue should not be empty, otherwise this function should "
                  "not have been called")
            return None


# WebSockets interface to the STT service
#
# note: an object of this class is created for each WebSocket
# connection, every time we call connectWS
class WSInterfaceProtocol(WebSocketClientProtocol):

    def __init__(self, factory, queue, summary, dirOutput, contentType):
        self.factory = factory
        self.queue = queue
        self.summary = summary
        self.dirOutput = dirOutput
        self.contentType = contentType
        self.packetRate = 20
        self.listeningMessages = 0
        self.timeFirstInterim = -1
        self.bytesSent = 0
        self.chunkSize = 2000     # in bytes
        super(self.__class__, self).__init__()
        print(dirOutput)
        print("contentType: {} queueSize: {}".format(self.contentType,
                                                     self.queue.qsize()))

    def setUtterance(self, utt):

        self.uttNumber = utt[0]
        self.uttFilename = utt[1]
        self.summary[self.uttNumber] = {"hypothesis": "",
                                        "status": {"code": "", "reason": ""}}
        self.fileJson = "{}/{}.json.txt".format(self.dirOutput, self.uttNumber)
        try:
            os.remove(self.fileJson)
        except OSError:
            pass

    # helper method that sends a chunk of audio if needed (as required
    # what the specified pacing is)
    def maybeSendChunk(self, data):

        def sendChunk(chunk, final=False):
            self.bytesSent += len(chunk)
            self.sendMessage(chunk, isBinary=True)
            if final:
                self.sendMessage(b'', isBinary=True)

        if (self.bytesSent + self.chunkSize >= len(data)):
            if (len(data) > self.bytesSent):
                sendChunk(data[self.bytesSent:len(data)], True)
                return
        sendChunk(data[self.bytesSent:self.bytesSent + self.chunkSize])
        self.factory.reactor.callLater(0.01, self.maybeSendChunk, data=data)
        return

    def onConnect(self, response):
        print("onConnect, server connected: {}".format(response.peer))

    def onOpen(self):
        print("onOpen")
        data = {"action": "start",
                "content-type": str(self.contentType),
                "continuous": True,
                "interim_results": True,
                "inactivity_timeout": 600,
                'max_alternatives': 3,
                'timestamps': True,
                'word_confidence': True}
        print("sendMessage(init)")
        # send the initialization parameters
        self.sendMessage(json.dumps(data).encode('utf8'))

        # start sending audio right away (it will get buffered in the
        # STT service)
        print(self.uttFilename)
        with open(str(self.uttFilename), 'rb') as f:
            self.bytesSent = 0
            dataFile = f.read()
        self.maybeSendChunk(dataFile)
        print("onOpen ends")

    def onMessage(self, payload, isBinary):

        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print(u"Text message received: {0}".format(payload.decode('utf8')))

            # if uninitialized, receive the initialization response
            # from the server
            jsonObject = json.loads(payload.decode('utf8'))
            if 'state' in jsonObject:
                self.listeningMessages += 1
                if self.listeningMessages == 2:
                    print("sending close 1000")
                    # close the connection
                    self.sendClose(1000)

            # if in streaming
            elif 'results' in jsonObject:
                jsonObject = json.loads(payload.decode('utf8'))
                hypothesis = ""
                # empty hypothesis
                if len(jsonObject['results']) == 0:
                    print("empty hypothesis!")
                # regular hypothesis
                else:
                    # dump the message to the output directory
                    jsonObject = json.loads(payload.decode('utf8'))
                    with open(self.fileJson, "a") as f:
                        f.write(json.dumps(jsonObject, indent=4,
                                           sort_keys=True))

                    res = jsonObject['results'][0]
                    hypothesis = res['alternatives'][0]['transcript']
                    bFinal = (res['final'] is True)
                    if bFinal:
                        print('final hypothesis: "' + hypothesis + '"')
                        self.summary[self.uttNumber]['hypothesis'] += hypothesis
                    else:
                        print('interim hyp: "' + hypothesis + '"')

    def onClose(self, wasClean, code, reason):

        print("onClose")
        print("WebSocket connection closed: {0}, code: {1}, clean: {2}, "
              "reason: {0}".format(reason, code, wasClean))
        self.summary[self.uttNumber]['status']['code'] = code
        self.summary[self.uttNumber]['status']['reason'] = reason

        # create a new WebSocket connection if there are still
        # utterances in the queue that need to be processed
        self.queue.task_done()

        if not self.factory.prepareUtterance():
            return

        # SSL client context: default
        if self.factory.isSecure:
            contextFactory = ssl.ClientContextFactory()
        else:
            contextFactory = None
        connectWS(self.factory, contextFactory)


# function to check that a value is a positive integer
def check_positive_int(value):
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError(
            '"%s" is an invalid positive int value' % value)
    return ivalue


# function to check the credentials format
def check_credentials(credentials):
    elements = credentials.split(":")
    if len(elements) == 2:
        return elements
    else:
        raise argparse.ArgumentTypeError(
            '"%s" is not a valid format for the credentials ' % credentials)


if __name__ == '__main__':

    # parse command line parameters
    parser = argparse.ArgumentParser(
        description=('client to do speech recognition using the WebSocket '
                     'interface to the Watson STT service'))
    parser.add_argument(
        '-credentials', action='store', dest='credentials',
        help="Basic Authentication credentials in the form 'username:password'",
        required=True, type=check_credentials)
    parser.add_argument(
        '-in', action='store', dest='fileInput', default='./recordings.txt',
        help='text file containing audio files')
    parser.add_argument(
        '-out', action='store', dest='dirOutput', default='./output',
        help='output directory')
    parser.add_argument(
        '-type', action='store', dest='contentType', default='audio/wav',
        help='audio content type, for example: \'audio/l16; rate=44100\'')
    parser.add_argument(
        '-model', action='store', dest='model', default='en-US_BroadbandModel',
        help='STT model that will be used')
    parser.add_argument(
        '-amcustom', action='store', dest='am_custom_id', default=None,
        help='id of the acoustic model customization that will be used', required=False)
    parser.add_argument(
        '-lmcustom', action='store', dest='lm_custom_id', default=None,
        help='id of the language model customization that will be used', required=False)
    parser.add_argument(
        '-threads', action='store', dest='threads', default='1',
        help='number of simultaneous STT sessions', type=check_positive_int)
    parser.add_argument(
        '-optout', action='store_true', dest='optOut',
        help=('specify opt-out header so user data, such as speech and '
              'hypotheses are not logged into the server'))
    parser.add_argument(
        '-tokenauth', action='store_true', dest='tokenauth',
        help='use token based authentication')

    args = parser.parse_args()

    # create output directory if necessary
    if os.path.isdir(args.dirOutput):
        fmt = 'the output directory "{}" already exists, overwrite? (y/n)? '
        while True:
            answer = raw_input(fmt.format(args.dirOutput)).strip().lower()
            if answer == "n":
                sys.stderr.write("exiting...")
                sys.exit()
            elif answer == "y":
                break
    else:
        os.makedirs(args.dirOutput)

    # logging
    log.startLogging(sys.stdout)

    # add audio files to the processing queue
    q = Queue.Queue()
    lines = [line.rstrip('\n') for line in open(args.fileInput)]
    fileNumber = 0
    for fileName in lines:
        print(fileName)
        q.put((fileNumber, fileName))
        fileNumber += 1

    hostname = "stream.watsonplatform.net"
    headers = {'X-WDC-PL-OPT-OUT': '1'} if args.optOut else {}

    # authentication header
    if args.tokenauth:
        headers['X-Watson-Authorization-Token'] = (
            Utils.getAuthenticationToken('https://' + hostname,
                                         'speech-to-text',
                                         args.credentials[0],
                                         args.credentials[1]))
    else:
        auth = args.credentials[0] + ":" + args.credentials[1]
        headers["Authorization"] = "Basic " + base64.b64encode(auth.encode()).decode('utf-8')

    print(headers)
    # create a WS server factory with our protocol
    fmt = "wss://{}/speech-to-text/api/v1/recognize?model={}"
    url = fmt.format(hostname, args.model)
    if args.am_custom_id != None:
        url += "&acoustic_customization_id=" + args.am_custom_id
    if args.lm_custom_id != None:
        url += "&customization_id=" + args.lm_custom_id
    print(url)
    summary = {}
    factory = WSInterfaceFactory(q, summary, args.dirOutput, args.contentType,
                                 args.model, url, headers, debug=False)
    factory.protocol = WSInterfaceProtocol

    for i in range(min(int(args.threads), q.qsize())):

        factory.prepareUtterance()

        # SSL client context: default
        if factory.isSecure:
            contextFactory = ssl.ClientContextFactory()
        else:
            contextFactory = None
        connectWS(factory, contextFactory)

    reactor.run()

    # dump the hypotheses to the output file
    fileHypotheses = args.dirOutput + "/hypotheses.txt"
    f = open(fileHypotheses, "w")
    successful = 0
    emptyHypotheses = 0
    print(sorted(summary.items()))
    counter = 0
    for key, value in enumerate(sorted(summary.items())):
        value = value[1]  
        if value['status']['code'] == 1000:
            print('{}: {} {}'.format(key, value['status']['code'],
                                     value['hypothesis'].encode('utf-8')))
            successful += 1
            if value['hypothesis'][0] == "":
                emptyHypotheses += 1
        else:
            fmt = '{}: {status[code]} REASON: {status[reason]}'
            print(fmt.format(key, **status))
        f.write('{}: {}\n'.format(counter + 1, value['hypothesis'].encode('utf-8')))
        counter += 1
    f.close()
    fmt = "successful sessions: {} ({} errors) ({} empty hypotheses)"
    print(fmt.format(successful, len(summary) - successful, emptyHypotheses))



























    #############################################################
    #!/usr/bin/env python
#
# Copyright 2016 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import base64
import configparser
import json
import threading
import time

import pyaudio
import websocket
from websocket._abnf import ABNF

CHUNK = 1024
FORMAT = pyaudio.paInt16
# Even if your default input is multi channel (like a webcam mic),
# it's really important to only record 1 channel, as the STT service
# does not do anything useful with stereo. You get a lot of "hmmm"
# back.
CHANNELS = 1
# Rate is important, nothing works without it. This is a pretty
# standard default. If you have an audio device that requires
# something different, change this.
RATE = 44100
RECORD_SECONDS = 5
FINALS = []

REGION_MAP = {
    'us-east': 'gateway-wdc.watsonplatform.net',
    'us-south': 'stream.watsonplatform.net',
    'eu-gb': 'stream.watsonplatform.net',
    'eu-de': 'stream-fra.watsonplatform.net',
    'au-syd': 'gateway-syd.watsonplatform.net',
    'jp-tok': 'gateway-syd.watsonplatform.net',
}


def read_audio(ws, timeout):
    """Read audio and sent it to the websocket port.
    This uses pyaudio to read from a device in chunks and send these
    over the websocket wire.
    """
    global RATE
    p = pyaudio.PyAudio()
    # NOTE(sdague): if you don't seem to be getting anything off of
    # this you might need to specify:
    #
    #    input_device_index=N,
    #
    # Where N is an int. You'll need to do a dump of your input
    # devices to figure out which one you want.
    RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")
    rec = timeout or RECORD_SECONDS

    for i in range(0, int(RATE / CHUNK * rec)):
        data = stream.read(CHUNK)
        # print("Sending packet... %d" % i)
        # NOTE(sdague): we're sending raw binary in the stream, we
        # need to indicate that otherwise the stream service
        # interprets this as text control messages.
        ws.send(data, ABNF.OPCODE_BINARY)

    # Disconnect the audio stream
    stream.stop_stream()
    stream.close()
    print("* done recording")

    # In order to get a final response from STT we send a stop, this
    # will force a final=True return message.
    data = {"action": "stop"}
    ws.send(json.dumps(data).encode('utf8'))
    # ... which we need to wait for before we shutdown the websocket
    time.sleep(1)
    ws.close()

    # ... and kill the audio device
    p.terminate()


def on_message(self, msg):
    """Print whatever messages come in.
    While we are processing any non trivial stream of speech Watson
    will start chunking results into bits of transcripts that it
    considers "final", and start on a new stretch. It's not always
    clear why it does this. However, it means that as we are
    processing text, any time we see a final chunk, we need to save it
    off for later.
    """
    data = json.loads(msg)
    if "results" in data:
        if data["results"][0]["final"]:
            FINALS.append(data)
        # This prints out the current fragment that we are working on
        print(data['results'][0]['alternatives'][0]['transcript'])


def on_error(self, error):
    """Print any errors."""
    print(error)


def on_close(ws):
    """Upon close, print the complete and final transcript."""
    transcript = "".join([x['results'][0]['alternatives'][0]['transcript']
                          for x in FINALS])
    print(transcript)


def on_open(ws):
    """Triggered as soon a we have an active connection."""
    args = ws.args
    data = {
        "action": "start",
        # this means we get to send it straight raw sampling
        "content-type": "audio/l16;rate=%d" % RATE,
        "continuous": True,
        "interim_results": True,
        # "inactivity_timeout": 5, # in order to use this effectively
        # you need other tests to handle what happens if the socket is
        # closed by the server.
        "word_confidence": True,
        "timestamps": True,
        "max_alternatives": 3
    }

    # Send the initial control message which sets expectations for the
    # binary stream that follows:
    ws.send(json.dumps(data).encode('utf8'))
    # Spin off a dedicated thread where we are going to read and
    # stream out audio.
    threading.Thread(target=read_audio,
                     args=(ws, args.timeout)).start()

def get_url():
    config = configparser.RawConfigParser()
    config.read('speech.cfg')
    # See
    # https://console.bluemix.net/docs/services/speech-to-text/websockets.html#websockets
    # for details on which endpoints are for each region.
    region = config.get('auth', 'region')
    host = REGION_MAP[region]
    return ("wss://{}/speech-to-text/api/v1/recognize"
           "?model=en-US_BroadbandModel").format(host)

def get_auth():
    config = configparser.RawConfigParser()
    config.read('speech.cfg')
    apikey = config.get('auth', 'apikey')
    return ("apikey", apikey)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Transcribe Watson text in real time')
    parser.add_argument('-t', '--timeout', type=int, default=5)
    # parser.add_argument('-d', '--device')
    # parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    return args


def main():
    # Connect to websocket interfaces
    headers = {}
    userpass = ":".join(get_auth())
    headers["Authorization"] = "Basic " + base64.b64encode(
        userpass.encode()).decode()
    url = get_url()

    # If you really want to see everything going across the wire,
    # uncomment this. However realize the trace is going to also do
    # things like dump the binary sound packets in text in the
    # console.
    #
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                header=headers,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.args = parse_args()
    # This gives control over the WebSocketApp. This is a blocking
    # call, so it won't return until the ws.close() gets called (after
    # 6 seconds in the dedicated thread).
    ws.run_forever()


if __name__ == "__main__":
    main()
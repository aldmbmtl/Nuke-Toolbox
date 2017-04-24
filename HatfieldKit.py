"""
Alex Hatfield's nuke tool kit
"""
# nuke imports
import nuke
import nukescripts

# PySide imports
from PySide import QtGui

# python imports
import os
import sys
from collections import OrderedDict


TRACED = []
FILE_FILTER = ['menu.py', 'init.py']


def traceImports(frame, event, arg):
    if event != 'call':
        return

    co = frame.f_code
    func_name = co.co_name
    if func_name == 'write':
        return

    caller = frame.f_back

    if not caller:
        return

    caller_filename = caller.f_code.co_filename
    path = os.path.dirname(caller_filename).replace('\\', '/').replace('//', '/')

    global TRACED

    if path in TRACED:
        return

    for f in FILE_FILTER:
        if f in os.listdir(path):
            TRACED.append(path)
            break
sys.settrace(traceImports)

# shows the import order for this pipeline
def showPipelineStructure():
    """
    Display the import order from the pipeline.
    :return:
    """
    p = nuke.Panel('Pipeline import order')
    for order, path in enumerate(TRACED):
        p.addSingleLineInput(str(order+1), path)
    p.show()
nuke.menu('Nuke').addCommand('Hatfield\'s/Pipeline/Import Order', showPipelineStructure)

# used in tandem with floating windows in the node graph. 
# Assigns a 'Close all' method to the alt+` hotkey combo so 
# you don't need to click close on all of them.
def closeAllNodes():
    """
    Closes all open nodes.
    """
    for node in nuke.allNodes():
        node.hideControlPanel()
nuke.menu('Node Graph').addCommand('Hatfield\'s/Close all nodes', closeAllNodes, 'alt+`')

# the default auto place fuction will always apply the snapping
# to all nodes. This version will only do it to the selected nodes
# if there are any. If nothing is selected, it reverts to the old
# method of snapping all nodes.
def smartSnap():
    selNodes = nuke.selectedNodes()
    if selNodes == []:
        for node in nuke.allNodes():
            nuke.autoplaceSnap(node)
    else:
        for node in selNodes:
            nuke.autoplaceSnap(node)
nuke.menu('Node Graph').addCommand('Autoplace', smartSnap, shortcut='\\')

# creates a dialog box that points to a read node in the comp. The read node that is selected
# will be hooked to a postage stamp. Really useful for huge comps.
def createReadLink():
    options = []
    for node in nuke.allNodes():
        node.setSelected(False)
        if node.Class() == 'Read':
            options.append(node.name() + ' ' + os.path.basename(node['file'].value()))

    result = nuke.choice('Create link to Read...', 'Pick a read', options)
    if result is None:
        return

    targetRead = nuke.toNode(options[result].split(' ')[0])
    postageStamp = nuke.createNode('PostageStamp', inpanel=False)
    postageStamp['label'].setValue('[basename [value [topnode].file]]')
    postageStamp['hide_input'].setValue(True)
    postageStamp.setInput(0, targetRead)
nuke.menu('Node Graph').addCommand('Hatfield\'s/Link to Read', createReadLink, shortcut='l')

# Just for shutting off callbacks if a studio overly loaded one up
# and is actively slowing shit down.
class CallbackManager(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'Callback Manager')
        self.addKnob(nuke.Text_Knob('onCreates', 'onCreates'))
        for key in nuke.onCreates.keys():
            func = str(list(nuke.onCreates[key][0])[0])
            command = 'nuke.onCreates.pop("%s") ; print nuke.onCreates' % (key)
            commandKnob = nuke.PyScript_Knob('killCommand', 'Remove: ' + func)
            commandKnob.setCommand(command)
            commandKnob.setFlag(0x00001000)
            
            self.addKnob(commandKnob)
            
        self.addKnob(nuke.Text_Knob('onDestroys', 'onDestroys'))
        for key in nuke.onDestroys.keys():
            func = str(list(nuke.onDestroys[key][0])[0])
            command = 'nuke.onDestroys.pop("%s")' % (key)
            commandKnob = nuke.PyScript_Knob('killCommand', 'Remove: ' + func)
            commandKnob.setCommand(command)
            commandKnob.setFlag(0x00001000)

            self.addKnob(commandKnob)
            
        self.addKnob(nuke.Text_Knob('onScriptCloses', 'onScriptCloses'))
        for key in nuke.onScriptCloses.keys():
            func = str(list(nuke.onScriptCloses[key][0])[0])
            command = 'nuke.onScriptCloses.pop("%s")' % (key)
            commandKnob = nuke.PyScript_Knob('killCommand', 'Remove: ' + func)
            commandKnob.setCommand(command)
            commandKnob.setFlag(0x00001000)

            self.addKnob(commandKnob)
            
        self.addKnob(nuke.Text_Knob('onScriptLoads', 'onScriptLoads'))
        for key in nuke.onScriptLoads.keys():
            func = str(list(nuke.onScriptLoads[key][0])[0])
            command = 'nuke.onScriptLoads.pop("%s")' % (key)
            commandKnob = nuke.PyScript_Knob('killCommand', 'Remove: ' + func)
            commandKnob.setCommand(command)
            commandKnob.setFlag(0x00001000)

            self.addKnob(commandKnob)
            
        self.addKnob(nuke.Text_Knob('onScriptSaves', 'onScriptSaves'))
        for key in nuke.onScriptSaves.keys():
            func = str(list(nuke.onScriptSaves[key][0])[0])
            command = 'nuke.onScriptSaves.pop("%s")' % (key)
            commandKnob = nuke.PyScript_Knob('killCommand', 'Remove: ' + func)
            commandKnob.setCommand(command)
            commandKnob.setFlag(0x00001000)

            self.addKnob(commandKnob)
            
        self.addKnob(nuke.Text_Knob('knobChangeds', 'knobChangeds'))
        for key in nuke.knobChangeds.keys():
            func = str(list(nuke.knobChangeds[key][0])[0])
            command = 'nuke.knobChangeds.pop("%s")' % (key)
            commandKnob = nuke.PyScript_Knob('killCommand', 'Remove: ' + func)
            commandKnob.setCommand(command)
            commandKnob.setFlag(0x00001000)

            self.addKnob(commandKnob)
nuke.menu('Nuke').addCommand('Hatfield\'s/Callback Manager', 'import HatfieldKit ; HatfieldKit.CallbackManager().show()')

# Breaks out a single layer to rgb and then shuffles it back into the source node.
def breakOutLayer():
    """
    Breaks out a layer to RGB and then shuffles it back in.
    :return:
    """
    node = nuke.selectedNode()

    layers = []

    for channel in node.channels():
        layer = channel.split('.')[0]

        if layer not in layers:
            layers.append(layer)

    index = nuke.choice('Break out layer...', 'Layer', layers)

    if index:
        anchor = nuke.nodes.Dot(xpos=node.xpos() + 34, ypos=node.ypos() + 150)
        anchor.setInput(0, node)

        shuffle = nuke.nodes.Shuffle(xpos=node.xpos() + 250, ypos=anchor.ypos() - 4)
        shuffle['in'].setValue(layers[index])
        shuffle.setInput(0, anchor)

        pipeAnchor = nuke.nodes.Dot(xpos=node.xpos() + 250 + 34, ypos=node.ypos() + 500)
        pipeAnchor.setInput(0, shuffle)

        shuffleCopy = nuke.nodes.ShuffleCopy(red='red', green='green', blue='blue', xpos=node.xpos(),
                                             ypos=node.ypos() + 500 - 4)
        shuffleCopy['out'].setValue(layers[index])
        shuffleCopy.setInput(0, anchor)
        shuffleCopy.setInput(1, pipeAnchor)
nuke.menu('Node Graph').addCommand('Hatfield\'s/Break out layer', breakOutLayer, 'ctrl+b')

"""
Hatfield Node Kisser. Simulates the node kissing function from Flame.
"""
# this is assigned to the 'shift+z' key stroke
def node_kisser():
    try:
        selNode = nuke.selectedNode()
    except ValueError:
        return

    xpos = selNode['xpos'].value()
    ypos = selNode['ypos'].value()

    connectedNodes = []

    for input_int in xrange(0, selNode.maxInputs()):
        pingedInput = selNode.input(input_int)

        if pingedInput is None:
            if input_int == selNode.optionalInput():
                continue
            else:
                break
        else:
            connectedNodes.append(pingedInput)

    possible_nodes = {}
    point = xpos + ypos

    for node in nuke.allNodes():
        if node == selNode or node in connectedNodes:
            continue

        thresh_range = 50
        ythresh_range = 100

        node_xpos = node['xpos'].value()
        node_ypos = node['ypos'].value()

        #top handles inputs
        if node_ypos <= ypos:
            if abs(node_ypos - ypos) <= ythresh_range:
                #left
                if node_xpos <= xpos:
                    if abs(node_xpos - xpos) <= thresh_range:
                        possible_nodes[abs((node_xpos + node_ypos) - point)] = node

                #right
                if node_xpos >= xpos:
                    if abs(node_xpos - xpos) <= thresh_range:
                        possible_nodes[abs((node_xpos + node_ypos) - point)] = node

    keys = possible_nodes.keys()
    keys.sort()
    try:
        selNode.setInput(input_int, possible_nodes[keys[0]])
    except:
        pass
nuke.menu('Node Graph').addCommand('Hatfield\'s/Kiss', node_kisser, 'shift+z')
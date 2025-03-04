
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from  qgis.core import *



# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .teste_buffer_dialog import Teste_Plugin_BufferDialog
import os.path
import processing 
import sys, os
from osgeo import ogr

class Teste_Plugin_Buffer:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Teste_Plugin_Buffer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Teste Plugin Buffer ')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Teste_Plugin_Buffer', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/teste_buffer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Exemplo Buffer '),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Teste Plugin Buffer '),
                action)
            self.iface.removeToolBarIcon(action)

    def CarregaVetor (self):
        """Preenche o combo box com as layers vetoriais do projeto no QGIS"""
        self.dlg.comboBox.clear()
        listaLayer= [layer for layer in QgsProject.instance().mapLayers().values()]
        listaLayerVetor = []
      
        for layer in listaLayer:    
            if layer.type()== QgsMapLayer.VectorLayer:
                listaLayerVetor.append(layer.name())
        self.dlg.comboBox.addItems(listaLayerVetor)    
     

    def AbriVetor (self):
        """"Janela de dialogo para abrir uma Layer a ser aplicada o Buffer"""
        camada_abrir = str(QFileDialog.getOpenFileName(caption="Escolha a camada ....", filter = "Shapefiles(*.shp)")[0] )     
     #se a camada abrir não for vazio
        if (camada_abrir != ""):
            self.iface.addVectorLayer(camada_abrir,str.split(os.path.basename(camada_abrir),".")[0], "ogr")
            self.CarregaVetor()
            
            
            
    def CamadaEntrada (self):
        #Definir a layer especifica do ComboBox
        
        layer= None
        nomeCamada = self.dlg.comboBox.currentText()
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name ()== nomeCamada:
                layer= lyr
                break 
        return layer

    def DefinirSaida(self):
             #Definimos o local onde será salvo o Buffer assim como o nome do arquivo
        camada_salvar = str(QFileDialog.getSaveFileName(caption="Defina a layer de saida ....", filter = "Shapefiles(*.shp)")[0] )        
        self.dlg.lineEdit.setText(camada_salvar)
        
        
    def variavais (self):
        #Define as variaveis a serem utilizadas na loica

        self.camada= self.CamadaEntrada()
        self.saida= self.dlg.lineEdit.text()
        self.largura = self.dlg.doubleSpinBox.value()
     
    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = Teste_Plugin_BufferDialog()

        # show the dialog
        self.dlg.show()
        
        #Add as funçoes
        self.CarregaVetor()
        self.dlg.toolButton.clicked.connect(self.AbriVetor)
        self.dlg.toolButton_2.clicked.connect(self.DefinirSaida)
        

        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Chamando as variaveis
            self.variavais()
            #criano o buffer usando o proprio QGIS
            
            buffer= processing.run("native:buffer",{'INPUT':self.camada,
            'DISTANCE':self.largura,
            'DISSOLVE': False,
            'END_CAP_STYLE': 0,
            'JOIN_STYLE': 0,
            'OUTPUT' : self.saida
            })
             
             
             #carregamos o resultado
            self.iface.addVectorLayer(self.saida,str.split(os.path.basename(self.saida),".")[0], "ogr")       
             
            pass

import wx
import requests
import threading
import urllib.parse

class ProgressDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Cargando", size=(200, 100))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        msg = wx.StaticText(panel, label="Cargando...")
        vbox.Add(msg, 1, wx.ALL | wx.CENTER, 5)
        panel.SetSizer(vbox)
        self.Center()

class BuscadorDirectoriosFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='GIANT FUZZIN', size=(400, 400))
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        url_box = wx.BoxSizer(wx.HORIZONTAL)
        url_label = wx.StaticText(panel, label='URL Base:')
        url_box.Add(url_label, 0, wx.ALL | wx.CENTER, 5)
        self.url_entry = wx.TextCtrl(panel)
        url_box.Add(self.url_entry, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(url_box, 0, wx.EXPAND)

        archivo_box = wx.BoxSizer(wx.HORIZONTAL)
        archivo_label = wx.StaticText(panel, label='Archivo de Directorios:')
        archivo_box.Add(archivo_label, 0, wx.ALL | wx.CENTER, 5)
        self.archivo_entry = wx.TextCtrl(panel)
        archivo_box.Add(self.archivo_entry, 1, wx.ALL | wx.EXPAND, 5)
        examinar_button = wx.Button(panel, label='Examinar')
        examinar_button.Bind(wx.EVT_BUTTON, self.examinar_archivo)
        archivo_box.Add(examinar_button, 0, wx.ALL | wx.CENTER, 5)
        vbox.Add(archivo_box, 0, wx.EXPAND)

        self.directorios_listbox = wx.ListBox(panel, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        vbox.Add(self.directorios_listbox, 1, wx.ALL | wx.EXPAND, 5)

        buttons_box = wx.BoxSizer(wx.HORIZONTAL)
        iniciar_button = wx.Button(panel, label='Iniciar Búsqueda')
        iniciar_button.Bind(wx.EVT_BUTTON, self.on_iniciar_busqueda)
        buttons_box.Add(iniciar_button, 0, wx.ALL, 5)

        exportar_button = wx.Button(panel, label='Exportar a TXT')
        exportar_button.Bind(wx.EVT_BUTTON, self.exportar_a_txt)
        buttons_box.Add(exportar_button, 0, wx.ALL, 5)

        vbox.Add(buttons_box, 0, wx.ALIGN_CENTER)

        panel.SetSizer(vbox)
        self.progress_dialog = None

    def examinar_archivo(self, event):
        with wx.FileDialog(self, "Abrir archivo", wildcard="Archivos de texto (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            self.archivo_entry.SetValue(pathname)

    def cargar_directorios_desde_archivo(self, archivo):
        try:
            with open(archivo, "r") as f:
                return [line.strip() for line in f]
        except FileNotFoundError:
            wx.MessageBox("No se pudo encontrar el archivo.", "Error", wx.OK | wx.ICON_ERROR)
            return []

    def buscar_directorio(self, url_base, directorios, archivo_directorios):
        self.directorios_listbox.Clear()
        self.directorios_listbox.Append("BUSCANDO...")
        directorio_encontrado = False
        
        for directorio in directorios:
            url = f"{url_base}/{directorio}"
            try:
                respuesta = requests.get(url, timeout=5)  # Timeout de 5 segundos
                if respuesta.status_code == 200:
                    self.directorios_listbox.Append(f"[+] Directorio encontrado: {url}")
                    directorio_encontrado = True
            except requests.RequestException as e:
                print(f"Error al realizar la solicitud a {url}: {e}")
        
        if not directorio_encontrado:
            wx.MessageBox(f"No se ha encontrado ningún directorio con el diccionario: {archivo_directorios}", "Error", wx.OK | wx.ICON_ERROR)
        
        self.directorios_listbox.Delete(0) # Eliminar el indicador de búsqueda al finalizar

    def iniciar_busqueda(self, url_base, archivo_directorios):
        directorios = self.cargar_directorios_desde_archivo(archivo_directorios)
        if directorios:
            self.buscar_directorio(url_base, directorios, archivo_directorios)
        if self.progress_dialog:
            self.progress_dialog.Destroy()

    def on_iniciar_busqueda(self, event):
        url_base = self.url_entry.GetValue()
        archivo_directorios = self.archivo_entry.GetValue()
        
        if not url_base or not archivo_directorios:
            wx.MessageBox("Por favor, rellene todos los campos.", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        parsed_url = urllib.parse.urlparse(url_base)
        if not parsed_url.scheme:
            wx.MessageBox("Por favor, ingrese una URL con un esquema válido (por ejemplo, http:// o https://).", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        self.progress_dialog = ProgressDialog(self)
        threading.Thread(target=self.iniciar_busqueda, args=(url_base, archivo_directorios)).start()

    def exportar_a_txt(self, event):
        directorios_encontrados = self.directorios_listbox.GetStrings()
        if directorios_encontrados:
            with wx.FileDialog(self, "Guardar archivo", wildcard="Archivos de texto (*.txt)|*.txt",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return

                pathname = fileDialog.GetPath()
                with open(pathname, "w") as f:
                    for directorio in directorios_encontrados:
                        f.write(directorio + "\n")
        else:
            wx.MessageBox("No hay directorios encontrados para exportar.", "Advertencia", wx.OK | wx.ICON_WARNING)

def main():
    app = wx.App(False)
    frame = BuscadorDirectoriosFrame()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()

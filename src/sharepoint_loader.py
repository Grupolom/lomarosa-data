"""
Módulo para cargar archivos desde SharePoint - Dashboard Inventario Lomarosa
"""

import os
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from datetime import datetime
import json
from pathlib import Path
from dotenv import load_dotenv

class SharePointLoader:
    """Clase para gestionar la carga de archivos desde SharePoint"""
    
    def __init__(self):
        """Inicializa la conexión con SharePoint usando credenciales del archivo .env"""
        load_dotenv()
        
        # Credenciales de SharePoint
        self.site_url = os.getenv('SHAREPOINT_SITE_URL')
        self.client_id = os.getenv('SHAREPOINT_CLIENT_ID')
        self.client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET')
        
        # Configuración de rutas
        self.folder_relative_url = os.getenv('SHAREPOINT_FOLDER_URL', '/Documentos compartidos/Inventarios')
        self.local_download_path = Path('data/raw')
        
        # Asegurar que existe el directorio local
        self.local_download_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar contexto de SharePoint
        if all([self.site_url, self.client_id, self.client_secret]):
            self.ctx = self._get_context()
        else:
            raise ValueError("Faltan credenciales de SharePoint en el archivo .env")
    
    def _get_context(self):
        """Crea el contexto de autenticación para SharePoint"""
        try:
            credentials = ClientCredential(self.client_id, self.client_secret)
            ctx = ClientContext(self.site_url).with_credentials(credentials)
            return ctx
        except Exception as e:
            print(f"❌ Error al crear contexto de SharePoint: {str(e)}")
            return None
    
    def download_files(self):
        """Descarga los archivos de inventario desde SharePoint"""
        try:
            # Obtener lista de archivos en la carpeta
            folder = self.ctx.web.get_folder_by_server_relative_url(self.folder_relative_url)
            files = folder.files
            self.ctx.load(files)
            self.ctx.execute_query()
            
            files_downloaded = []
            for file in files:
                if file.name.endswith('.xlsx'):
                    local_path = self.local_download_path / file.name
                    
                    # Verificar si necesitamos actualizar el archivo
                    should_download = True
                    if local_path.exists():
                        local_modified = datetime.fromtimestamp(local_path.stat().st_mtime)
                        sharepoint_modified = file.time_last_modified
                        should_download = sharepoint_modified > local_modified
                    
                    if should_download:
                        print(f"📥 Descargando {file.name}...")
                        with open(local_path, "wb") as local_file:
                            file_content = File.open_binary(self.ctx, file.serverRelativeUrl)
                            local_file.write(file_content.content)
                        files_downloaded.append(file.name)
                        print(f"✅ Archivo guardado en {local_path}")
            
            return files_downloaded
            
        except Exception as e:
            print(f"❌ Error al descargar archivos: {str(e)}")
            return []
    
    def get_last_modified_info(self):
        """Obtiene información de última modificación de los archivos"""
        try:
            folder = self.ctx.web.get_folder_by_server_relative_url(self.folder_relative_url)
            files = folder.files
            self.ctx.load(files)
            self.ctx.execute_query()
            
            info = {}
            for file in files:
                if file.name.endswith('.xlsx'):
                    info[file.name] = {
                        'last_modified': file.time_last_modified.strftime('%Y-%m-%d %H:%M:%S'),
                        'size': file.length
                    }
            return info
            
        except Exception as e:
            print(f"❌ Error al obtener información de archivos: {str(e)}")
            return {}
    
    def monitor_changes(self, callback=None):
        """Monitorea cambios en los archivos de SharePoint"""
        try:
            last_check = {}
            while True:
                current_info = self.get_last_modified_info()
                
                # Detectar cambios
                for filename, info in current_info.items():
                    if filename not in last_check or last_check[filename]['last_modified'] != info['last_modified']:
                        print(f"🔄 Detectado cambio en {filename}")
                        if callback:
                            callback(filename)
                
                last_check = current_info
                time.sleep(300)  # Revisar cada 5 minutos
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoreo detenido")
        except Exception as e:
            print(f"❌ Error en monitoreo: {str(e)}")

if __name__ == "__main__":
    # Ejemplo de uso
    loader = SharePointLoader()
    files = loader.download_files()
    print("\n📋 Archivos descargados:")
    for file in files:
        print(f"  • {file}")
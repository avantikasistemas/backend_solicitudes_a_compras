from Utils.tools import Tools, CustomException
from sqlalchemy import text, or_, case
from sqlalchemy.sql import select
from collections import defaultdict
import json

class Querys:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.query_params = dict()

    # Query para obtener los tipos de estado para la cotizacion
    # def get_negociadores(self):

    #     try:
    #         response = list()
    #         sql = """
    #             SELECT DISTINCT u.des_usuario, dph.usuario AS creador_oc
    #             FROM dbo.documentos_ped_historia AS dph
    #             INNER JOIN dbo.usuarios AS u ON dph.usuario = u.usuario
    #             WHERE dph.sw = 3
    #             AND dph.fecha BETWEEN '20241101' AND '20501231'
    #             AND dph.bodega <> 99
    #             AND dph.usuario <> 'JAMARTINEZ'
    #             ORDER BY u.des_usuario;
    #         """

    #         query = self.db.execute(text(sql)).fetchall()
    #         if query:
    #             for key in query:
    #                 response.append({
    #                     "des_usuario": key[0].upper(),
    #                     "usuario": key[1]
    #                 })

    #         return response
                
    #     except Exception as ex:
    #         print(str(ex))
    #         raise CustomException(str(ex))
    #     finally:
    #         self.db.close()

    # Query para obtener los tipos de estado para la cotizacion
    def get_negociadores(self):

        try:
            response = list()
            sql = """
                SELECT des_usuario, usuario FROM negociadores;
            """

            query = self.db.execute(text(sql)).fetchall()
            if query:
                for key in query:
                    response.append({
                        "des_usuario": key[0].upper(),
                        "usuario": key[1]
                    })

            return response
                
        except Exception as ex:
            print(str(ex))
            raise CustomException(str(ex))
        finally:
            self.db.close()

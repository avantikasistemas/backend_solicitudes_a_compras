from Utils.tools import Tools, CustomException
from Utils.querys import Querys
from datetime import datetime
import json

class Formacion:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)
        self.FORM = 'FORM-'

    # Función para guardar una formación
    def guardar_formacion(self, data: dict):

        try:
            codigo = ''
            competencias = list()
            data_compe_insert = dict()
            data_macro_insert = dict()
            data_cargo_insert = dict()
            data_ciudad_insert = dict()
            
            lista_competencia_corporativa = data["lista_competencia_corporativa"]
            lista_competencia_rol = data["lista_competencia_rol"]
            lista_competencia_posicion = data["lista_competencia_posicion"]
            lista_macroprocesos = data["lista_macroprocesos"]
            lista_cargos = data["lista_cargos"]
            lista_ciudades = data["lista_ciudades"]
            lista_origenes = data["origen"]
            lista_evaluaciones = data["evaluacion"]
            
            if (not lista_competencia_corporativa or not lista_competencia_rol
                or not lista_competencia_posicion or not lista_macroprocesos
                or not lista_cargos or not lista_ciudades 
                or not lista_origenes or not lista_evaluaciones):
                
                raise CustomException(
                    "Ninguna de las listas puede estar vacía.")
                
            if (not data["modalidad"] or not data["tipo"]):
                raise CustomException(
                    "Modalidad o Tipo no deben estar vacíos.")
            
            # Consultamos el numero siguiente en el consecutivo.
            num_siguiente = self.querys.buscar_numero_siguiente()
            if num_siguiente:
                codigo = f"{self.FORM}{num_siguiente}"
            data["codigo"] = codigo
            data["created_at"] = datetime.today()
            
            # Eliminamos las listas de los datos de entrada ya que no se 
            # insertan en la tabla principal
            data.pop("lista_competencia_corporativa")
            data.pop("lista_competencia_rol")
            data.pop("lista_competencia_posicion")
            data.pop("lista_macroprocesos")
            data.pop("lista_cargos")
            data.pop("lista_ciudades")
            
            # Llenamos una sola lista con todas las competencias
            competencias.extend(lista_competencia_corporativa)
            competencias.extend(lista_competencia_rol)
            competencias.extend(lista_competencia_posicion)
            
            estado_formacion = 1
            if data["fecha_inicio"] and data["fecha_fin"]:
                estado_formacion = 2
                
            data["estado_formacion"] = estado_formacion
            
            data["origen"] = json.dumps(lista_origenes)
            data["evaluacion"] = json.dumps(lista_evaluaciones)

            # Guardamos los datos de la formación.
            formacion_id = self.querys.guardar_formacion(data)

            # Validamos si el registro fue exitoso, aumentamos el consecutivo.
            if formacion_id:
                
                for compe in competencias:
                    data_compe_insert = {
                        "formacion_id": formacion_id,
                        "tipo_competencia_id": compe,
                        "created_at": datetime.today(),
                    }
                    self.querys.guardar_competencias(data_compe_insert)
                    
                for macro in lista_macroprocesos:
                    data_macro_insert = {
                        "formacion_id": formacion_id,
                        "macroproceso_id": macro,
                        "created_at": datetime.today(),
                    }
                    self.querys.guardar_macroprocesos(data_macro_insert)

                for cargo in lista_cargos:
                    data_cargo_insert = {
                        "formacion_id": formacion_id,
                        "cargo_id": cargo,
                        "created_at": datetime.today(),
                    }
                    self.querys.guardar_cargos(data_cargo_insert)

                for ciudad in lista_ciudades:
                    data_ciudad_insert = {
                        "formacion_id": formacion_id,
                        "ciudad_id": ciudad,
                        "created_at": datetime.today(),
                    }
                    self.querys.guardar_ciudades(data_ciudad_insert)
                
                self.querys.actualizar_consecutivo(num_siguiente+1)

            # Retornamos la información.
            msg = f"Formación guardada exitosamente con el código: {codigo}"
            return self.tools.output(201, msg, data)

        except Exception as e:
            print(f"Error al guardar registro de formación: {e}")
            raise CustomException("Error al guardar registro de formación.")

    # Función para obtener las formaciones creadas
    def get_formaciones(self, data: dict):

        try:

            valor = data["valor"]

            # Acá usamos la query para traer la información get_proveedores
            formaciones = self.querys.get_formaciones(valor)

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", formaciones)

        except Exception as e:
            print(f"Error al obtener información de formaciones: {e}")
            raise CustomException("Error al obtener información de formaciones.")

    # Función para obtener las formaciones por id
    def get_formacion_by_id(self, data: dict):

        try:

            formacion_id = data["formacion_id"]

            # Llamamos a la función que trae la información de la formación.
            data_formacion = self.querys.get_formacion_by_id(formacion_id)

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", data_formacion)

        except Exception as e:
            print(f"Error al obtener información de formaciones: {e}")
            raise CustomException("Error al obtener información de formaciones.")

    # Función para actualizar una formación
    def actualizar_formacion(self, data: dict):

        try:
            msg = "La formación ya se encuentra finalizada y no se puede editar."
            # Separamos la formación id de la data de entrada.
            formacion_id = int(data.pop("formacion_id"))
            
            # Buscamos si la formación ya se encuentra finalizada y si es así
            # No dejamos que actualice más.
            formacion = self.querys.obtener_estado_formacion(formacion_id)
            if formacion:
                if formacion.estado_formacion == 3:
                    raise CustomException(msg)
            
            # Llamamos a la query que realiza el actualizado.
            self.querys.actualizar_formacion(formacion_id, data)

            # Retornamos la información.
            msg = f"Formación actualizada exitosamente."
            return self.tools.output(200, msg)

        except Exception as e:
            print(f"Error al actualizar registro de formación: {e}")
            raise CustomException(msg)

    # Función para guardar una formación
    def guardar_personal_formacion(self, data: dict):

        try:
            
            formacion_id = data["formacion_id"]
            personal = data["personal"]
            
            # Buscamos si la formación ya se encuentra finalizada y si es así
            # No dejamos que actualice más.
            formacion = self.querys.obtener_estado_formacion(formacion_id)
            if formacion:
                msg = "La formación ya se encuentra finalizada y no se puede editar."
                if formacion.estado_formacion == 3:
                    raise CustomException(msg)
            
            self.querys.desactivar_personal_x_formacion(formacion_id)
            
            if not personal:
                # Retornamos mensaje de no guardado
                msg = f"No hay personal a guardar."
                return self.tools.output(200, msg, data)
            
            for key in personal:
                data_guardar = {
                    "formacion_id": formacion_id,
                    "nit": key["cedula"],
                    "created_at": datetime.today(),
                }
                self.querys.guardar_personal_formacion(data_guardar)

            # Retornamos la información.
            msg = f"Personal guardado exitosamente."
            return self.tools.output(200, msg)

        except Exception as e:
            print(f"Error al guardar registro de formación: {e}")
            raise CustomException(msg)

    # Función para guardar una formación
    def obtener_personal_seleccionado_formacion(self, data: dict):

        try:
            
            formacion_id = data["formacion_id"]
            
            personal = self.querys.get_personal_formacion(formacion_id)

            # Retornamos la información.
            msg = "Datos encontrados."
            return self.tools.output(200, msg, personal)

        except Exception as e:
            print(f"Error al obtener datos de personal: {e}")
            raise CustomException("Error al obtener datos de personal.")

    # Función para actualizar los macroprocesos de una formación
    def actualizar_macroprocesos(self, data: dict):

        try:
            data_macro_insert = dict()
            data_cargo_insert = dict()

            formacion_id = data["formacion_id"]
            lista_macroprocesos = data["lista_macroprocesos"]
            lista_cargos = data["lista_cargos"]
            
            # Buscamos si la formación ya se encuentra finalizada y si es así
            # No dejamos que actualice más.
            formacion = self.querys.obtener_estado_formacion(formacion_id)
            if formacion:
                msg = "La formación ya se encuentra finalizada y no se puede editar."
                if formacion.estado_formacion == 3:
                    raise CustomException(msg)

            
            if (not lista_macroprocesos or not lista_cargos):
                msg = "Ninguna de las listas puede estar vacía."
                raise CustomException(msg)

            # Desactivamos los macroprocesos actuales,                
            self.querys.desactivar_macro_y_cargo_x_id(formacion_id)

            for macro in lista_macroprocesos:
                data_macro_insert = {
                    "formacion_id": formacion_id,
                    "macroproceso_id": macro,
                    "created_at": datetime.today(),
                }
                self.querys.guardar_macroprocesos(data_macro_insert)

            for cargo in lista_cargos:
                data_cargo_insert = {
                    "formacion_id": formacion_id,
                    "cargo_id": cargo,
                    "created_at": datetime.today(),
                }
                self.querys.guardar_cargos(data_cargo_insert)

            # Retornamos la información.
            msg = f"Formación actualizada exitosamente."
            return self.tools.output(200, msg, data)

        except Exception as e:
            print(f"Error al guardar registro de formación: {e}")
            raise CustomException(msg)

    # Función para consultar los datos de busqueda en modulo CONSULTAR
    def consultar_datos(self, data: dict):
        
        # Asignamos nuestros datos de entrada a sus respectivas variables
        codigo = data["codigo"]
        tema = data["tema"]

        try:
            if codigo:
                data["codigo"] = codigo.strip()

            if tema:
                data["tema"] = tema.strip()

            if data["position"] <= 0:
                message = "El campo posición no es válido"
                raise CustomException(message)

            datos_form = self.querys.consultar_datos(data)

            registros = datos_form["registros"]
            cant_registros = datos_form["cant_registros"]

            if not registros:
                message = "No hay listado de reportes que mostrar."
                return self.tools.output(200, message, data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 0,
                "registros": []
            })

            if cant_registros%data["limit"] == 0:
                total_pag = cant_registros//data["limit"]
            else:
                total_pag = cant_registros//data["limit"] + 1

            if total_pag < int(data["position"]):
                message = "La posición excede el número total de registros."
                return self.tools.output(200, message, data={
                "total_registros": 0,
                "total_pag": 0,
                "posicion_pag": 0,
                "registros": []
            })

            registros_dict = {
                "total_registros": cant_registros,
                "total_pag": total_pag,
                "posicion_pag": data["position"],
                "registros": registros
            }

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", registros_dict)

        except Exception as e:
            print(f"Error al obtener información de orden de compra: {e}")
            raise CustomException("Error al obtener información de orden de compra.")

    # Función para guardar las calificaciones de una persona y formacion
    def guardar_calificacion(self, data: dict):

        try:
            msg = "Error al guardar notas"
                        
            # Buscamos si la formación ya se encuentra finalizada y si es así
            data_calificacion  = self.querys.buscar_y_actualizar_calificacion(data)
            if data_calificacion:
                # Retornamos la información.
                msg = f"Notas actualizadas exitosamente."
                return self.tools.output(200, msg)
            
            data["created_at"] = datetime.now()
            data_save = self.querys.guardar_calificacion(data)
            if data_save:
                # Retornamos la información.
                msg = f"Notas guardadas exitosamente."
                return self.tools.output(200, msg)

        except Exception as e:
            print(f"Error al guardar notas: {e}")
            raise CustomException(msg)

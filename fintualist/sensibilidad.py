# simulacion_sensibilidad.py (actualizado con Pandas)
import pandas as pd
from fintualist.escenarios import (
    EscenarioArriendo,
    EscenarioCompra,
    ParametrosSimulacion,
)
from typing import Dict, Any


class SimuladorSensibilidad:
    def __init__(
        self, num_simulaciones: int, distribuciones_parametros: Dict[str, Any]
    ):
        """
        Inicializa el simulador de sensibilidad.

        Args:
            num_simulaciones: El número de simulaciones a realizar.
            distribuciones_parametros: Un diccionario donde las claves son los nombres
                                       de los parámetros (de ParametrosSimulacion)
                                       y los valores son objetos que tienen un
                                       método 'rvs' para generar muestras aleatorias.
        """
        self.num_simulaciones = num_simulaciones
        self.distribuciones_parametros = distribuciones_parametros
        self.resultados_df = pd.DataFrame()

    def _generar_parametros(self) -> ParametrosSimulacion:
        """
        Genera un diccionario de parámetros muestreados aleatoriamente
        para la simulación.

        Returns:
            Un objeto ParametrosSimulacion con los parámetros generados.
        """
        parametros = {}
        for nombre, distribucion in self.distribuciones_parametros.items():
            parametros[nombre] = distribucion.rvs()
        return ParametrosSimulacion(**parametros)

    def ejecutar_simulacion(self):
        """
        Ejecuta la simulación de sensibilidad para el número de simulaciones definido.
        """
        resultados_arriendo = []
        resultados_compra = []
        parametros_simulaciones = []
        for _ in range(self.num_simulaciones):
            # Generar parámetros aleatorios
            parametros = self._generar_parametros()

            parametros_simulaciones.append(parametros.model_dump())

            escenario_arriendo = EscenarioArriendo()
            resultado_arriendo = escenario_arriendo.calcular_capital_relativo_final(
                parametros
            )
            resultados_arriendo.append(resultado_arriendo)

            escenario_compra = EscenarioCompra()
            resultado_compra = escenario_compra.calcular_capital_relativo_final(
                parametros
            )
            resultados_compra.append(resultado_compra)

        self.resultados_df = pd.DataFrame(parametros_simulaciones)
        self.resultados_df["capital_relativo_arriendo"] = resultados_arriendo
        self.resultados_df["capital_relativo_compra"] = resultados_compra

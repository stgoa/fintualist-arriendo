# escenarios.py
import numpy_financial as npf
from pydantic import BaseModel


class ParametrosSimulacion(BaseModel):
    anios: int = 25
    tasa_rentabilidad: float = 0.05
    precio_propiedad: float = 5000
    porcentaje_pie: float = 0.20
    tasa_hipotecaria: float = 0.0340
    porcentaje_arriendo: float = 0.0038
    tasa_plusvalia: float = 0.0120
    porcentaje_remodelaciones: float = 0.0050
    avaluo_exento: float = 1256
    avaluo_cambio_tramo: float = 4424
    tasa_contribuciones_tramo1: float = 0.0093
    tasa_contribuciones_tramo2: float = 0.0109


class Escenario:
    """Clase base para los escenarios de compra y arriendo."""

    def calcular_valor_futuro(self, tasa, periodos, valor_presente=0, pago=0):
        """Calcula el valor futuro de una inversión."""
        return npf.fv(tasa, periodos, -pago, -valor_presente)

    def calcular_pago_mensual(self, tasa_anual, num_anios, principal):
        """Calcula el pago mensual de un préstamo."""
        tasa_mensual = tasa_anual / 12
        num_periodos = num_anios * 12
        return -npf.pmt(tasa_mensual, num_periodos, principal)

    def calcular_tasa_efectiva_anual_contribuciones(
        self,
        precio_propiedad,
        avaluo_exento,
        avaluo_cambio_tramo,
        tasa_tramo1,
        tasa_tramo2,
    ):
        """Calcula la tasa efectiva anual de contribuciones."""
        if precio_propiedad > avaluo_cambio_tramo:
            contribuciones_tramo2 = (tasa_tramo2 - tasa_tramo1) * (
                precio_propiedad - avaluo_cambio_tramo
            )
        else:
            contribuciones_tramo2 = 0

        if precio_propiedad > avaluo_exento:
            contribuciones_tramo1 = tasa_tramo1 * (precio_propiedad - avaluo_exento)
        else:
            contribuciones_tramo1 = 0

        return (contribuciones_tramo1 + contribuciones_tramo2) / precio_propiedad


class EscenarioArriendo(Escenario):
    """Escenario para el caso de arriendo."""

    def _calcular_valor_futuro_pie(self, params: ParametrosSimulacion):
        pie_inicial = params.precio_propiedad * params.porcentaje_pie
        return self.calcular_valor_futuro(
            params.tasa_rentabilidad, params.anios, valor_presente=pie_inicial
        )

    def _calcular_arriendo_mensual(self, params: ParametrosSimulacion):
        return params.porcentaje_arriendo * params.precio_propiedad

    def _calcular_valor_futuro_delta_dividendo(self, params: ParametrosSimulacion):
        monto_credito = params.precio_propiedad * (1 - params.porcentaje_pie)
        pago_mensual_dividendo = self.calcular_pago_mensual(
            params.tasa_hipotecaria, params.anios, monto_credito
        )
        pago_mensual_arriendo = self._calcular_arriendo_mensual(params)
        delta_mensual = pago_mensual_dividendo - pago_mensual_arriendo
        tasa_mensual_compuesta = (1 + params.tasa_rentabilidad) ** (1 / 12) - 1
        return self.calcular_valor_futuro(
            tasa_mensual_compuesta, params.anios * 12, pago=delta_mensual
        )

    def calcular_capital_relativo_final(self, params: ParametrosSimulacion):
        vf_pie = self._calcular_valor_futuro_pie(params)
        vf_delta = self._calcular_valor_futuro_delta_dividendo(params)
        return vf_pie + vf_delta


class EscenarioCompra(Escenario):
    """Escenario para el caso de compra."""

    def _calcular_valor_futuro_propiedad(self, params: ParametrosSimulacion):
        return self.calcular_valor_futuro(
            params.tasa_plusvalia, params.anios, valor_presente=params.precio_propiedad
        )

    def _calcular_valor_futuro_contribuciones(self, params: ParametrosSimulacion):
        tasa_efectiva_contribuciones = self.calcular_tasa_efectiva_anual_contribuciones(
            params.precio_propiedad,
            params.avaluo_exento,
            params.avaluo_cambio_tramo,
            params.tasa_contribuciones_tramo1,
            params.tasa_contribuciones_tramo2,
        )
        costo_trimestral_contribuciones = (
            tasa_efectiva_contribuciones * params.precio_propiedad
        ) / 4
        tasa_trimestral_compuesta = (1 + params.tasa_rentabilidad) ** (1 / 4) - 1
        return self.calcular_valor_futuro(
            tasa_trimestral_compuesta,
            params.anios * 4,
            pago=costo_trimestral_contribuciones,
        )

    def _calcular_valor_futuro_remodelaciones(self, params: ParametrosSimulacion):
        costo_anual_remodelaciones = (
            params.porcentaje_remodelaciones * params.precio_propiedad
        )
        return self.calcular_valor_futuro(
            params.tasa_rentabilidad, params.anios, pago=costo_anual_remodelaciones
        )

    def calcular_capital_relativo_final(self, params: ParametrosSimulacion):
        vf_propiedad = self._calcular_valor_futuro_propiedad(params)
        vf_contribuciones = self._calcular_valor_futuro_contribuciones(params)
        vf_remodelaciones = self._calcular_valor_futuro_remodelaciones(params)
        return vf_propiedad - vf_contribuciones - vf_remodelaciones

# test_escenarios.py
from fintualist.escenarios import (
    EscenarioArriendo,
    EscenarioCompra,
    ParametrosArriendo,
    ParametrosCompra,
    Escenario,
)
import numpy as np


class TestEscenarioArriendo:
    def test_capital_relativo_final_articulo(self):
        params_articulo = ParametrosArriendo(
            precio_propiedad=5000,
            porcentaje_pie=0.20,
            tasa_hipotecaria=0.0340,
            porcentaje_arriendo=0.0038,
            anios=25,
            tasa_rentabilidad=0.0531,
        )
        escenario_arriendo = EscenarioArriendo()
        resultado = escenario_arriendo.calcular_capital_relativo_final(params_articulo)
        valor_esperado = 4142
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=0)

    def test_valor_futuro_pie(self):
        params = ParametrosArriendo(
            precio_propiedad=5000,
            porcentaje_pie=0.20,
            tasa_rentabilidad=0.0531,
            anios=25,
        )
        escenario = EscenarioArriendo()
        resultado = escenario._calcular_valor_futuro_pie(params)
        valor_esperado = 3645.36  # Calculado manualmente
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=2)

    def test_valor_futuro_delta_dividendo(self):
        params = ParametrosArriendo(
            precio_propiedad=5000,
            porcentaje_pie=0.20,
            tasa_hipotecaria=0.0340,
            porcentaje_arriendo=0.0038,
            anios=25,
            tasa_rentabilidad=0.0531,
        )
        escenario = EscenarioArriendo()
        resultado = escenario._calcular_valor_futuro_delta_dividendo(params)
        valor_esperado = 496.56  # Calculado manualmente
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=2)

    def test_pago_mensual_arriendo_equivalente(self):
        params = ParametrosArriendo(precio_propiedad=5000, porcentaje_arriendo=0.0038)
        escenario = EscenarioArriendo()
        resultado = escenario._calcular_arriendo_mensual(params)
        valor_esperado = 19.00
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=2)

    def test_pago_mensual_dividendo(self):
        params = ParametrosArriendo(
            precio_propiedad=5000,
            porcentaje_pie=0.20,
            tasa_hipotecaria=0.0340,
            anios=25,
        )
        escenario = Escenario()
        monto_credito = params.precio_propiedad * (1 - params.porcentaje_pie)
        resultado = escenario.calcular_pago_mensual(
            params.tasa_hipotecaria, params.anios, monto_credito
        )
        valor_esperado = 19.81
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=2)


class TestEscenarioCompra:
    def test_capital_relativo_final_articulo(self):
        params_articulo = ParametrosCompra(
            precio_propiedad=5000,
            porcentaje_pie=0.20,
            tasa_plusvalia=0.0120,
            porcentaje_remodelaciones=0.0050,
            avaluo_exento=33664775 / 26799.01,
            avaluo_cambio_tramo=118571329 / 26799.01,
            tasa_contribuciones_tramo1=0.00933,
            tasa_contribuciones_tramo2=0.01088,
            anios=25,
            tasa_rentabilidad=0.0531,
        )
        escenario_compra = EscenarioCompra()
        resultado = escenario_compra.calcular_capital_relativo_final(params_articulo)
        valor_esperado = 3672
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=0)

    def test_valor_futuro_propiedad(self):
        params = ParametrosCompra(
            precio_propiedad=5000, tasa_plusvalia=0.0120, anios=25
        )
        escenario = EscenarioCompra()
        resultado = escenario._calcular_valor_futuro_propiedad(params)
        valor_esperado = 6737.25  # Calculado manualmente
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=2)

    def test_valor_futuro_contribuciones(self):
        params = ParametrosCompra(
            precio_propiedad=5000,
            avaluo_exento=33664775 / 26799.01,
            avaluo_cambio_tramo=118571329 / 26799.01,
            tasa_contribuciones_tramo1=0.00933,
            tasa_contribuciones_tramo2=0.01088,
            tasa_rentabilidad=0.0531,
            anios=25,
        )
        escenario = EscenarioCompra()
        resultado = escenario._calcular_valor_futuro_contribuciones(params)
        valor_esperado = 1819.738  # Calculado manualmente
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=2)

    def test_valor_futuro_remodelaciones(self):
        params = ParametrosCompra(
            precio_propiedad=5000,
            porcentaje_remodelaciones=0.0050,
            tasa_rentabilidad=0.0531,
            anios=25,
        )
        escenario = EscenarioCompra()
        resultado = escenario._calcular_valor_futuro_remodelaciones(params)
        valor_esperado = 1245.46  # Calculado manualmente
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=1)

    def test_tasa_efectiva_anual_contribuciones(self):
        params = ParametrosCompra(
            precio_propiedad=5000,
            avaluo_exento=33664775 / 26799.01,
            avaluo_cambio_tramo=118571329 / 26799.01,
            tasa_contribuciones_tramo1=0.00933,
            tasa_contribuciones_tramo2=0.01088,
            tasa_rentabilidad=0.0531,
            anios=25,
        )
        escenario = Escenario()
        resultado = escenario.calcular_tasa_efectiva_anual_contribuciones(
            params.precio_propiedad,
            params.avaluo_exento,
            params.avaluo_cambio_tramo,
            params.tasa_contribuciones_tramo1,
            params.tasa_contribuciones_tramo2,
        )
        valor_esperado = 0.007164355946730870000000  # Calculado manualmente
        np.testing.assert_almost_equal(resultado, valor_esperado, decimal=6)

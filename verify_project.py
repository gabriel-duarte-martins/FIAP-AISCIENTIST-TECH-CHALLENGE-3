"""Run Python File: executa testes de pesos, partições e contrato dos atributos."""
import unittest
from pathlib import Path

if __name__=='__main__':
    suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent/'tests'))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)

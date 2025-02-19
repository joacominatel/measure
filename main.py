#!/usr/bin/env python3
"""
Benchmark de procesamiento en Python

Este script ejecuta distintas pruebas de rendimiento para medir la capacidad de procesamiento
de la CPU utilizando cálculos intensivos. Se realizan pruebas en single-thread y en paralelo 
(con hilos y procesos) para obtener un panorama comparativo.
"""

import time
import random
import math
import threading
import multiprocessing
import statistics
import argparse
import logging
from typing import Callable, Tuple, List

# Configuración del logging para mostrar información en la consola
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def benchmark_math(duration: int = 10) -> Tuple[int, float]:
    """
    Ejecuta operaciones matemáticas intensivas durante 'duration' segundos.
    
    Retorna:
        - Total de operaciones realizadas.
        - Duración exacta de la prueba.
    """
    start = time.perf_counter()
    operations = 0
    while time.perf_counter() - start < duration:
        a = random.random()
        b = random.random()
        c = random.random()
        try:
            result = math.sqrt(a**2 + b**2) + math.sin(c) + math.log(a + 1)
        except ValueError:
            result = 0
        result = math.pow(result, 1.5) if result > 0 else 0
        operations += 1
    elapsed = time.perf_counter() - start
    return operations, elapsed

def benchmark_integer(duration: int = 10) -> Tuple[int, float]:
    """
    Ejecuta operaciones aritméticas con enteros durante 'duration' segundos.
    
    Retorna:
        - Total de operaciones realizadas.
        - Duración exacta de la prueba.
    """
    start = time.perf_counter()
    operations = 0
    while time.perf_counter() - start < duration:
        a = random.randint(1, 1000)
        b = random.randint(1, 1000)
        c = random.randint(1, 1000)
        result = (a * b) + (a * c) - (b * c)
        result *= (a + b + c)
        operations += 1
    elapsed = time.perf_counter() - start
    return operations, elapsed

def worker_benchmark(duration: int, results: List[int], calc_function: Callable[[int], Tuple[int, float]]) -> None:
    """
    Función worker para ser ejecutada en un hilo.
    Ejecuta la función de benchmark especificada y almacena el número de operaciones en 'results'.
    """
    ops, _ = calc_function(duration)
    results.append(ops)

def threaded_benchmark(duration: int = 10, num_threads: int = 4,
                       calc_function: Callable[[int], Tuple[int, float]] = benchmark_math) -> Tuple[int, float, int]:
    """
    Ejecuta la función de benchmark en múltiples hilos.
    
    Retorna:
        - Total de operaciones acumuladas de todos los hilos.
        - Duración total de la prueba.
        - Número de hilos utilizados.
    """
    threads: List[threading.Thread] = []
    results: List[int] = []
    start = time.perf_counter()
    for _ in range(num_threads):
        t = threading.Thread(target=worker_benchmark, args=(duration, results, calc_function))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    total_ops = sum(results)
    elapsed = time.perf_counter() - start
    return total_ops, elapsed, num_threads

def process_worker(duration: int, queue: multiprocessing.Queue,
                   calc_function: Callable[[int], Tuple[int, float]]) -> None:
    """
    Función worker para ser ejecutada en un proceso.
    Ejecuta la función de benchmark y coloca el resultado en una cola.
    """
    ops, _ = calc_function(duration)
    queue.put(ops)

def multiprocess_benchmark(duration: int = 10, num_processes: int = 4,
                           calc_function: Callable[[int], Tuple[int, float]] = benchmark_math) -> Tuple[int, float, int]:
    """
    Ejecuta la función de benchmark en múltiples procesos.
    
    Retorna:
        - Total de operaciones acumuladas de todos los procesos.
        - Duración total de la prueba.
        - Número de procesos utilizados.
    """
    processes: List[multiprocessing.Process] = []
    queue = multiprocessing.Queue()
    start = time.perf_counter()
    for _ in range(num_processes):
        p = multiprocessing.Process(target=process_worker, args=(duration, queue, calc_function))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    total_ops = 0
    while not queue.empty():
        total_ops += queue.get()
    elapsed = time.perf_counter() - start
    return total_ops, elapsed, num_processes

def run_series(test_function: Callable, test_name: str, series: int = 3, duration: int = 10, **kwargs) -> List[float]:
    """
    Ejecuta múltiples series de pruebas utilizando la función de benchmark especificada.
    
    Para cada serie se muestra:
        - Total de operaciones realizadas.
        - Tiempo empleado y operaciones/segundo (ops/seg).
    
    Retorna:
        - Una lista con los valores de rendimiento (ops/seg) de cada prueba.
    """
    logging.info(f"\nSerie de pruebas: {test_name}")
    results: List[float] = []
    for i in range(series):
        result = test_function(duration, **kwargs)
        # Diferenciamos entre pruebas single-thread y pruebas en paralelo (multihilo/multiproceso)
        if len(result) == 2:
            ops, dur = result
            extra_info = ""
        else:
            ops, dur, extra_val = result
            extra_info = f"({extra_val} hilos/procesos)"
        ops_per_sec = ops / dur if dur > 0 else 0
        results.append(ops_per_sec)
        logging.info(f"  Prueba {i+1}: {ops} operaciones en {dur:.2f} seg -> {ops_per_sec:.2f} ops/seg {extra_info}")
    avg = statistics.mean(results)
    stdev = statistics.stdev(results) if len(results) > 1 else 0.0
    logging.info(f"  Promedio: {avg:.2f} ops/seg, Desviación estándar: {stdev:.2f} ops/seg")
    return results

def main():
    parser = argparse.ArgumentParser(description="Benchmark de procesamiento en Python")
    parser.add_argument("--duration", type=int, default=10, help="Duración de cada prueba en segundos")
    parser.add_argument("--series", type=int, default=3, help="Número de series a ejecutar para cada test")
    parser.add_argument("--threads", type=int, default=4, help="Número de hilos para pruebas multihilo")
    parser.add_argument("--processes", type=int, default=4, help="Número de procesos para pruebas multiproceso")
    args = parser.parse_args()

    logging.info("=== Benchmark de Procesamiento en Python ===")
    
    # Pruebas single-thread
    math_results = run_series(benchmark_math, "Operaciones matemáticas (single-thread)", args.series, args.duration)
    int_results = run_series(benchmark_integer, "Aritmética entera (single-thread)", args.series, args.duration)
    
    # Prueba multihilo (para cargas que puedan beneficiarse de la concurrencia, aunque el GIL limita en CPU-bound)
    threaded_results = run_series(threaded_benchmark,
                                  f"Operaciones matemáticas en {args.threads} hilos",
                                  args.series, args.duration,
                                  num_threads=args.threads, calc_function=benchmark_math)
    
    # Prueba multiproceso (para aprovechar todos los núcleos en tareas CPU-bound)
    multiprocess_results = run_series(multiprocess_benchmark,
                                      f"Operaciones matemáticas en {args.processes} procesos",
                                      args.series, args.duration,
                                      num_processes=args.processes, calc_function=benchmark_math)
    
    # Resumen general
    logging.info("\n=== Resumen General ===")
    logging.info("Operaciones matemáticas (single-thread): Promedio: {:.2f} ops/seg".format(statistics.mean(math_results)))
    logging.info("Aritmética entera (single-thread): Promedio: {:.2f} ops/seg".format(statistics.mean(int_results)))
    logging.info("Operaciones matemáticas (multihilo, {} hilos): Promedio: {:.2f} ops/seg".format(args.threads, statistics.mean(threaded_results)))
    logging.info("Operaciones matemáticas (multiproceso, {} procesos): Promedio: {:.2f} ops/seg".format(args.processes, statistics.mean(multiprocess_results)))

if __name__ == '__main__':
    main()

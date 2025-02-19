import time, random, math, threading

def benchmark_math(duration=10):
    """
    Prueba de operaciones matemáticas: realiza cálculos con números flotantes
    para generar una carga de trabajo intensa.
    Retorna el total de operaciones y la duración.
    """
    start = time.time()
    operations = 0
    while time.time() - start < duration:
        a = random.random()
        b = random.random()
        c = random.random()
        result = math.sqrt(a**2 + b**2) + math.sin(c) + math.log(a + 1)
        result = math.pow(result, 1.5) if result > 0 else 0
        operations += 1
    return operations, duration

def benchmark_integer(duration=10):
    """
    Prueba de aritmética entera: realiza operaciones con números enteros.
    Retorna el total de operaciones y la duración.
    """
    start = time.time()
    operations = 0
    while time.time() - start < duration:
        a = random.randint(1, 1000)
        b = random.randint(1, 1000)
        c = random.randint(1, 1000)
        result = (a * b) + (a * c) - (b * c)
        result = result * (a + b + c)
        operations += 1
    return operations, duration

def worker_benchmark(duration, results, calc_function):
    """
    Función worker para ser ejecutada en cada hilo.
    Ejecuta la función de prueba (calc_function) y almacena el número de operaciones realizadas.
    """
    ops, _ = calc_function(duration)
    results.append(ops)

def threaded_benchmark(duration=10, num_threads=4, calc_function=benchmark_math):
    """
    Ejecuta en paralelo (en varios hilos) la función de prueba especificada.
    Retorna el total de operaciones acumuladas de todos los hilos, la duración
    y el número de hilos utilizados.
    """
    threads = []
    results = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker_benchmark, args=(duration, results, calc_function))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    total_ops = sum(results)
    return total_ops, duration, num_threads

def run_series(test_function, test_name, series=3, duration=10, **kwargs):
    """
    Ejecuta varias series de pruebas usando la función test_function.
    Imprime el número total de operaciones y el rendimiento en operaciones/segundo.
    """
    print(f"\nSerie de pruebas: {test_name}")
    results = []
    for i in range(series):
        result = test_function(duration, **kwargs)
        if len(result) == 2:
            ops, dur = result
            extra = ""
        else:
            ops, dur, extra_val = result
            extra = f"({extra_val} hilos)"
        ops_per_sec = ops / dur
        results.append(ops_per_sec)
        print(f"  Prueba {i+1}: {ops} operaciones en {dur} seg -> {ops_per_sec:.2f} ops/seg {extra}")
    average = sum(results) / len(results)
    print(f"  Promedio: {average:.2f} ops/seg")
    return results

def main():
    duration = 10   # Duración de cada prueba en segundos
    series = 3      # Número de series a ejecutar

    print("=== Benchmark de CPU y Aritmética ===")
    
    # 1. Prueba con operaciones matemáticas (flotantes)
    math_results = run_series(benchmark_math, "Operaciones matemáticas", series, duration)

    # 2. Prueba con aritmética entera
    int_results = run_series(benchmark_integer, "Aritmética entera", series, duration)

    # 3. Prueba multihilo usando operaciones matemáticas (por ejemplo, con 4 hilos)
    num_threads = 4
    threaded_results = run_series(threaded_benchmark, 
                                  f"Operaciones matemáticas en {num_threads} hilos", 
                                  series, duration, 
                                  num_threads=num_threads, calc_function=benchmark_math)

    # Resumen de resultados
    print("\n=== Resumen General ===")
    print("Operaciones matemáticas (single-thread):")
    print("   Promedio: {:.2f} ops/seg".format(sum(math_results)/len(math_results)))
    print("Aritmética entera (single-thread):")
    print("   Promedio: {:.2f} ops/seg".format(sum(int_results)/len(int_results)))
    print("Operaciones matemáticas (multihilo, {} hilos):".format(num_threads))
    print("   Promedio (suma de hilos): {:.2f} ops/seg".format(sum(threaded_results)/len(threaded_results)))
    
if __name__ == '__main__':
    main()

from ortools.sat.python import cp_model
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/optimize")
def optimize():
    # ===== Datos =====
    tecnicos = ["T1", "T2"]
    servicios = ["S1", "S2", "S3"]
    habilidades_tecnicos = {
        "T1": ["Fibra Óptica", "Routers"],
        "T2": ["Fibra Óptica", "Configuración de Red"]
    }
    habilidades_servicios = {
        "S1": ["Fibra Óptica"],
        "S2": ["Routers"],
        "S3": ["Fibra Óptica", "Configuración de Red"]
    }

    # ===== Modelo =====
    model = cp_model.CpModel()

    # Variables de decisión
    asignaciones = {}
    for tecnico in tecnicos:
        for servicio in servicios:
            asignaciones[(tecnico, servicio)] = model.NewBoolVar(f"asignacion_{tecnico}_{servicio}")

    # Cada servicio debe ser asignado a exactamente un técnico
    for servicio in servicios:
        model.Add(sum(asignaciones[(tecnico, servicio)] for tecnico in tecnicos) == 1)

    # Los técnicos deben tener las habilidades requeridas
    for tecnico in tecnicos:
        for servicio in servicios:
            if not set(habilidades_servicios[servicio]).issubset(set(habilidades_tecnicos[tecnico])):
                model.Add(asignaciones[(tecnico, servicio)] == 0)

    # Objetivo (igual que tu ejemplo)
    model.Minimize(sum(asignaciones[(t, s)] for t in tecnicos for s in servicios))

    # ===== Solver =====
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return jsonify({"status": "INFEASIBLE"}), 400

    # Construir salida de texto (como si "imprimiéramos" la solución)
    lineas = ["Solución:"]
    for servicio in servicios:
        asignado = False
        for tecnico in tecnicos:
            if solver.Value(asignaciones[(tecnico, servicio)]) == 1:
                lineas.append(f"Servicio {servicio} asignado a técnico {tecnico}")
                asignado = True
                break
        if not asignado:
            lineas.append(f"Servicio {servicio}: sin asignación")

    texto = "\n".join(lineas)
    return Response(texto, mimetype="text/plain")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
    print("Solución:")
    for servicio in servicios:
        for tecnico in tecnicos:
            if solver.Value(asignaciones[(tecnico, servicio)]) == 1:
                print(f"Servicio {servicio} asignado a técnico {tecnico}")
            else:
                print("No se encontró una solución factible.")
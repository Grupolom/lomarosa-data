// ==========================================
// VARIABLES GLOBALES
// ==========================================

let file1Obj = null;
let file2Obj = null;
let recordatoriosGlobal = [];

// ==========================================
// UTILIDADES
// ==========================================

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ==========================================
// DRAG & DROP
// ==========================================

function setupDragAndDrop() {
    const dropZoneTerceros = document.getElementById("dropZoneTerceros");
    const dropZoneCartera = document.getElementById("dropZoneCartera");
    const fileTercerosInput = document.getElementById("fileTerceros");
    const fileCarteraInput = document.getElementById("fileCartera");

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Configurar zona 1
    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
        dropZoneTerceros.addEventListener(eventName, preventDefaults, false);
    });

    ["dragenter", "dragover"].forEach(eventName => {
        dropZoneTerceros.addEventListener(eventName, () => {
            dropZoneTerceros.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZoneTerceros.addEventListener(eventName, () => {
            dropZoneTerceros.classList.remove("dragover");
        });
    });

    dropZoneTerceros.addEventListener("drop", e => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile1(files[0]);
        }
    });

    fileTercerosInput.addEventListener("change", e => {
        if (e.target.files.length > 0) {
            handleFile1(e.target.files[0]);
        }
    });

    // Configurar zona 2
    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
        dropZoneCartera.addEventListener(eventName, preventDefaults, false);
    });

    ["dragenter", "dragover"].forEach(eventName => {
        dropZoneCartera.addEventListener(eventName, () => {
            dropZoneCartera.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZoneCartera.addEventListener(eventName, () => {
            dropZoneCartera.classList.remove("dragover");
        });
    });

    dropZoneCartera.addEventListener("drop", e => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile2(files[0]);
        }
    });

    fileCarteraInput.addEventListener("change", e => {
        if (e.target.files.length > 0) {
            handleFile2(e.target.files[0]);
        }
    });
}

function handleFile1(file) {
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
        alert("Por favor selecciona un archivo Excel (.xlsx o .xls)");
        return;
    }

    file1Obj = file;

    const info = document.getElementById("infoTerceros");
    info.innerHTML = `<strong>✓ Archivo cargado:</strong><br>${file.name}<br><small>${formatFileSize(file.size)}</small>`;
    info.style.display = "block";

    document.getElementById("dropZoneTerceros").classList.add("file-loaded");

    checkFilesReady();
}

function handleFile2(file) {
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
        alert("Por favor selecciona un archivo Excel (.xlsx o .xls)");
        return;
    }

    file2Obj = file;

    const info = document.getElementById("infoCartera");
    info.innerHTML = `<strong>✓ Archivo cargado:</strong><br>${file.name}<br><small>${formatFileSize(file.size)}</small>`;
    info.style.display = "block";

    document.getElementById("dropZoneCartera").classList.add("file-loaded");

    checkFilesReady();
}

function checkFilesReady() {
    const btnAnalizar = document.getElementById("btnAnalizar");

    if (file1Obj && file2Obj) {
        btnAnalizar.disabled = false;
    } else {
        btnAnalizar.disabled = true;
    }
}

// ==========================================
// ANALIZAR ARCHIVOS (ENVIAR AL BACKEND)
// ==========================================

async function analizarArchivos() {
    const btnAnalizar = document.getElementById("btnAnalizar");
    btnAnalizar.disabled = true;
    btnAnalizar.textContent = "Procesando...";

    try {
        // Crear FormData con ambos archivos
        const formData = new FormData();
        formData.append("file1", file1Obj);
        formData.append("file2", file2Obj);

        // Enviar al backend
        const response = await fetch("/procesar-excel", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || "Error al procesar archivos");
        }

        const resultado = await response.json();

        if (!resultado.success) {
            throw new Error(resultado.message || "Error desconocido");
        }

        recordatoriosGlobal = resultado.recordatorios || [];

        if (recordatoriosGlobal.length === 0) {
            alert("No se encontraron facturas próximas a vencer o vencidas con email asignado.");
            btnAnalizar.disabled = false;
            btnAnalizar.textContent = "Analizar Archivos";
            return;
        }

        // Renderizar tabla y estadísticas
        renderTablaRecordatorios();
        renderEstadisticas(resultado.stats);

        // Mostrar pasos 2 y 3
        document.getElementById("step2").style.display = "block";
        document.getElementById("step3").style.display = "block";

        // Scroll suave al paso 2
        document.getElementById("step2").scrollIntoView({ behavior: "smooth" });

        btnAnalizar.textContent = "Analizar Archivos";
        btnAnalizar.disabled = false;

    } catch (error) {
        console.error("Error al analizar archivos:", error);
        alert("Error al procesar los archivos:\n\n" + error.message);
        btnAnalizar.disabled = false;
        btnAnalizar.textContent = "Analizar Archivos";
    }
}

// ==========================================
// RENDER DE TABLA Y ESTADÍSTICAS
// ==========================================

function renderTablaRecordatorios() {
    const tbody = document.querySelector("#tablaRecordatorios tbody");
    tbody.innerHTML = "";

    // Ordenar: primero vencidos, luego próximos
    const ordenados = recordatoriosGlobal.sort((a, b) => {
        if (a.estado === "vencido" && b.estado !== "vencido") return -1;
        if (a.estado !== "vencido" && b.estado === "vencido") return 1;
        return a.dias - b.dias;
    });

    ordenados.forEach(r => {
        const tr = document.createElement("tr");

        const estadoTexto = r.estado === "vencido" ? "🔴 Vencido" : "⚠️ Próximo";

        tr.innerHTML = `
            <td><span class="badge ${r.badge_class}">${estadoTexto}</span></td>
            <td>${r.nombre_tercero || "N/A"}</td>
            <td>${r.email || "N/A"}</td>
            <td class="monospace">${r.numero_factura || "N/A"}</td>
            <td>${r.fecha_vencimiento || "N/A"}</td>
            <td class="monospace">${r.dias}</td>
            <td class="monospace">${r.saldo || "N/A"}</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderEstadisticas(stats) {
    document.getElementById("statProximos").textContent = stats.proximos || 0;
    document.getElementById("statVencidos").textContent = stats.vencidos || 0;
    document.getElementById("statTotal").textContent = stats.total || 0;
    document.getElementById("totalCorreos").textContent = stats.total || 0;
}

// ==========================================
// ENVÍO DE CORREOS
// ==========================================

async function enviarCorreos() {
    if (recordatoriosGlobal.length === 0) {
        alert("No hay recordatorios para enviar.");
        return;
    }

    const confirmacion = confirm(
        `¿Estás seguro de enviar ${recordatoriosGlobal.length} correos de recordatorio?\n\nEsta acción no se puede deshacer.`
    );

    if (!confirmacion) return;

    const btnEnviar = document.getElementById("btnEnviarCorreos");
    btnEnviar.disabled = true;
    btnEnviar.textContent = "Enviando...";

    // Mostrar área de progreso
    const progressArea = document.getElementById("progressArea");
    progressArea.style.display = "block";

    const progressFill = document.getElementById("progressFill");
    const progressText = document.getElementById("progressText");

    progressFill.style.width = "0%";
    progressText.textContent = "Preparando envío...";

    try {
        // Simular progreso inicial
        progressFill.style.width = "20%";
        progressText.textContent = "Enviando correos...";

        // Hacer POST a /enviar-correos
        const response = await fetch("/enviar-correos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                recordatorios: recordatoriosGlobal
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || "Error en la respuesta del servidor");
        }

        const resultado = await response.json();

        // Actualizar barra de progreso
        progressFill.style.width = "100%";
        progressText.textContent = "Envío completado";

        // Ocultar progreso después de 1 segundo
        setTimeout(() => {
            progressArea.style.display = "none";
        }, 1000);

        // Mostrar resultados
        mostrarResultados(resultado);

        btnEnviar.textContent = "Enviar Correos Ahora";
        btnEnviar.disabled = false;

    } catch (error) {
        console.error("Error al enviar correos:", error);
        alert("Error al enviar correos:\n\n" + error.message);

        progressText.textContent = "Error en el envío";
        progressFill.style.width = "0%";

        btnEnviar.textContent = "Enviar Correos Ahora";
        btnEnviar.disabled = false;
    }
}

function mostrarResultados(resultado) {
    const resultsArea = document.getElementById("resultsArea");
    resultsArea.style.display = "block";

    // Actualizar resumen
    document.getElementById("resultExitosos").textContent = resultado.exitosos || 0;
    document.getElementById("resultFallidos").textContent = resultado.fallidos || 0;

    // Renderizar tabla de detalles
    const tbody = document.querySelector("#tablaResultados tbody");
    tbody.innerHTML = "";

    if (resultado.resultados && resultado.resultados.length > 0) {
        resultado.resultados.forEach(r => {
            const tr = document.createElement("tr");
            const badgeClass = r.success ? "badge-success" : "badge-error";
            const estadoText = r.success ? "✓ Enviado" : "✗ Fallido";
            const mensaje = r.error || "Correo enviado exitosamente";

            tr.innerHTML = `
                <td><span class="badge ${badgeClass}">${estadoText}</span></td>
                <td>${r.nombre_tercero || "N/A"}</td>
                <td>${r.destinatario || "N/A"}</td>
                <td class="monospace">${r.numero_factura || "N/A"}</td>
                <td>${mensaje}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Scroll a resultados
    resultsArea.scrollIntoView({ behavior: "smooth" });
}

// ==========================================
// INICIALIZACIÓN
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    setupDragAndDrop();

    document.getElementById("btnAnalizar").addEventListener("click", analizarArchivos);
    document.getElementById("btnEnviarCorreos").addEventListener("click", enviarCorreos);

    console.log("App inicializada correctamente");
    console.log("URL: http://localhost:5000");
});

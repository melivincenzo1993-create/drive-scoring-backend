@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Drive Scoring — Analisi Solvibilità</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: #f8fafc;
                --card-bg: #ffffff;
                --text-main: #0f172a;
                --text-muted: #64748b;
                --border-color: #e2e8f0;
                --primary: #10b981;
                --primary-hover: #059669;
                --accent-warn: #fef3c7;
                --text-warn: #d97706;
                --border-warn: #fde68a;
            }}
            
            body {{ 
                font-family: 'Inter', sans-serif; 
                background-color: var(--bg-color); 
                margin: 0; 
                padding: 40px 20px; 
                color: var(--text-main);
                -webkit-font-smoothing: antialiased;
            }}
            
            .container {{ 
                background: var(--card-bg); 
                max-width: 580px; 
                margin: 0 auto; 
                padding: 40px; 
                border-radius: 16px; 
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.02), 0 8px 10px -6px rgba(0, 0, 0, 0.03);
                border: 1px solid var(--border-color);
            }}
            
            h1 {{ 
                text-align: center; 
                color: var(--text-main); 
                font-size: 26px;
                font-weight: 700;
                letter-spacing: -0.02em;
                margin-bottom: 8px; 
            }}
            
            p.subtitle {{ 
                text-align: center; 
                color: var(--text-muted); 
                font-size: 15px;
                margin-top: 0;
                margin-bottom: 35px; 
            }}
            
            .form-group {{ 
                margin-bottom: 24px; 
                display: flex; 
                flex-direction: column; 
            }}
            
            label {{ 
                font-weight: 500; 
                margin-bottom: 8px; 
                font-size: 14px; 
                color: var(--text-main);
            }}
            
            input[type="text"], input[type="number"], input[type="date"], input[type="email"], select {{ 
                padding: 12px 14px; 
                border: 1px solid var(--border-color); 
                border-radius: 8px; 
                font-size: 15px; 
                font-family: inherit;
                width: 100%; 
                box-sizing: border-box;
                background-color: #fff;
                color: var(--text-main);
                transition: border-color 0.2s, box-shadow 0.2s;
            }}
            
            input:focus, select:focus {{
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
            }}
            
            input[type="file"] {{ 
                padding: 8px 0; 
                font-family: inherit;
                font-size: 14px;
                color: var(--text-muted);
            }}
            
            .optional-text {{ 
                font-weight: 400; 
                color: var(--text-muted); 
                font-size: 12px; 
                margin-left: 4px;
            }}
            
            .btn {{ 
                background-color: var(--primary); 
                color: white; 
                padding: 15px; 
                border: none; 
                border-radius: 8px; 
                font-weight: 600; 
                font-size: 16px; 
                cursor: pointer; 
                width: 100%; 
                margin-top: 15px; 
                transition: background-color 0.2s, transform 0.1s; 
                font-family: inherit;
            }}
            
            .btn:hover {{ 
                background-color: var(--primary-hover); 
            }}
            
            .btn:active {{
                transform: scale(0.99);
            }}
            
            .disclaimer-box {{ 
                background-color: var(--accent-warn); 
                color: var(--text-warn); 
                border: 1px solid var(--border-warn); 
                padding: 16px 20px; 
                border-radius: 8px; 
                font-size: 13px; 
                line-height: 1.6; 
                margin-bottom: 35px; 
                text-align: justify; 
            }}
            
            .footer {{ 
                text-align: center; 
                margin-top: 30px; 
                font-size: 13px; 
            }}
            
            .footer a {{ 
                color: var(--text-muted); 
                text-decoration: none; 
                border-bottom: 1px solid var(--border-color);
                transition: color 0.2s, border-color 0.2s;
                padding-bottom: 2px;
            }}
            
            .footer a:hover {{ 
                color: var(--primary); 
                border-color: var(--primary);
            }}
        </style>
        <script>
            function updateFormFields() {{
                var profile = document.getElementById("target_profile").value;
                var lavoroDipendente = document.getElementById("gruppo-dipendente");
                var lavoroPiva = document.getElementById("gruppo-piva");
                var docLabel = document.getElementById("doc-label");
                
                if (profile === "pensionato") {{
                    lavoroDipendente.style.display = "none";
                    lavoroPiva.style.display = "none";
                    docLabel.innerHTML = "Cedolino della Pensione / CUD <span class='optional-text'>(Opzionale)</span>";
                }} else if (profile === "libero_professionista") {{
                    lavoroDipendente.style.display = "none";
                    lavoroPiva.style.display = "flex";
                    docLabel.innerHTML = "Modello Redditi (Ex Unico) / Cassetto Fiscale <span class='optional-text'>(Opzionale)</span>";
                }} else {{
                    lavoroDipendente.style.display = "flex";
                    lavoroPiva.style.display = "none";
                    docLabel.innerHTML = "Documento di Reddito <span class='optional-text'>(Opzionale - Ultima busta paga)</span>";
                }}
            }}
            window.onload = function() {{ updateFormFields(); }};
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Analisi Solvibilità Multi-Profilo</h1>
            <p class="subtitle">Seleziona il profilo di destinazione e calcola l'affidabilità finanziaria.</p>
            
            <div class="disclaimer-box">
                <strong>Nota informativa importante:</strong> {DISCLAIMER_TEXT}
            </div>

            <form action="/score/privato" method="POST" enctype="multipart/form-data">
                
                <div class="form-group">
                    <label>Profilo di Destinazione (Profilo Richiedente)</label>
                    <select name="target_profile" id="target_profile" onchange="updateFormFields()" required>
                        <option value="privato_dipendente">Privato (Dipendente)</option>
                        <option value="libero_professionista">Libero professionista / Ditta individuale</option>
                        <option value="pensionato">Pensionato</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Email Utente</label>
                    <input type="email" name="user_email" required placeholder="esempio@email.com">
                </div>

                <div class="form-group">
                    <label>Tipologia Prodotto</label>
                    <select name="product_type" required>
                        <option value="finanziamento">Finanziamento</option>
                        <option value="leasing">Leasing</option>
                        <option value="NLT">NLT (Noleggio a Lungo Termine)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Durata Contratto (in mesi)</label>
                    <input type="number" name="contract_duration_months" required placeholder="Es. 36">
                </div>

                <div class="form-group">
                    <label>Rata Mensile Stimata (€)</label>
                    <input type="number" step="0.01" name="estimated_monthly_rate" required placeholder="Es. 250">
                </div>

                <div class="form-group">
                    <label>Anticipo Iniziale (€)</label>
                    <input type="number" step="0.01" name="initial_down_payment" required placeholder="Es. 1000">
                </div>

                <div class="form-group">
                    <label>Debiti/Rate Mensili Attuali (€)</label>
                    <input type="number" step="0.01" name="current_monthly_debts" required placeholder="Se nessuno metti 0">
                </div>

                <div class="form-group">
                    <label>Segnalazioni o Insolvenze Passate?</label>
                    <select name="has_credit_issues" required>
                        <option value="false">No (Nessun problema passato)</option>
                        <option value="true">Sì (Presenza di segnalazioni CRIF)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Data di Nascita</label>
                    <input type="date" name="birth_date" required>
                </div>

                <div id="gruppo-dipendente">
                    <div class="form-group" style="width:100%;">
                        <label>Tipo di Contratto di Lavoro</label>
                        <select name="contract_type">
                            <option value="indeterminato">Tempo Indeterminato</option>
                            <option value="determinato">Tempo Determinato</option>
                        </select>
                    </div>
                    <div class="form-group" style="width:100%;">
                        <label>Settore Lavorativo Datore</label>
                        <input type="text" name="employer_sector" placeholder="Es. Pubblico, Privato, Metalmeccanico">
                    </div>
                </div>

                <div id="gruppo-piva" style="display:none; flex-direction:column; width:100%;">
                    <div class="form-group">
                        <label>Anno inizio attività (Apertura Partita IVA)</label>
                        <input type="number" name="piva_start_year" placeholder="Es. 2020" min="1950" max="2026">
                    </div>
                </div>

                <div class="form-group">
                    <label>Reddito Mensile Netto Medio (€)</label>
                    <input type="number" step="0.01" name="net_monthly_income" required placeholder="Es. 1800">
                </div>

                <div class="form-group">
                    <label id="doc-label">Documento di Reddito</label>
                    <input type="file" name="documento_reddito" accept=".pdf, .png, .jpg, .jpeg">
                </div>

                <button type="submit" class="btn">Calcola Score Solvibilità</button>
            </form>
            
            <div class="footer">
                <a href="/docs">Accedi alla Documentazione API Tecnica</a>
            </div>
        </div>
    </body>
    </html>
    """

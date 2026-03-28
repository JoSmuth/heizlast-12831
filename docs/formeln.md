# Formelreferenz — Heizlastberechnung nach DIN EN 12831-1

## Transmissionswärmeverluste

### Wärmebrückenzuschlag (Gl. 1)

ΔU_TB,k = (Σ(Ψ_l · l_l) + Σχ_m) / A_k

Pauschalwerte: Kat. A=0.05, B=0.10, C=0.15, D=0.20 W/(m²K)

### Wärmeübertragung unbeheizte Räume (Gl. 2)

H_T,iae = Σ(A_k · (U_k + ΔU_TB,k) · f_ia,k)

### Äquivalenter U-Wert Erdreich (Gl. 3)

U_equiv,k = a / (b + (c₁ + B')^n₁ + (c₂ + z)^n₂ + (c₃ + U_k + ΔU_TB)^n₃ + d)

B' = A_g / (0.5 · P)

### Transmissionsverlustkoeffizient (Gl. 7)

H_T,12 = Σ(A_k · U_eff,k · f_x)

## Lüftungswärmeverluste

### Infiltration (Gl. 32)

q_v,env = (q_env,50 · A_env + q_v,open) · f_qv,z · f_dir

### Mindestluftwechsel

q_v,min = 0.5 · V_i

### Lüftungsverlust (Gl. 32-34) — ρ·c_p = 0,34 Wh/(m³K)

Φ_V,env = 0,34 · q_v,env · (θ_int − θ_e)

Φ_V,sup = 0,34 · q_v,sup · (θ_int − θ_rec,z)

Φ_V,transfer = 0,34 · q_v,transfer · (θ_int − θ_transfer)

### WRG (§6.3.3.7)

θ_rec,z = θ_e + η_rec · (θ_exh − θ_e)

## Zeitkonstante (§6.3.5)

τ = C_eff / (H_T + H_V) [h]

Korrektur: θ_e,korrigiert = θ_e + Δθ_τ (max. +4 K)

## Zuschläge

### Komfort (Gl. 43)

ΔΦ_comf = Φ_HL(θ_comf) − Φ_HL(θ_stand)

### Kombination (Gl. 44)

Wenn ΔΦ_comf < 0: ΔΦ = ΔΦ_comf + Φ_hu

Sonst: ΔΦ = max(ΔΦ_comf, Φ_hu)

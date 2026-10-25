import csv
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from io import StringIO

from fastapi import FastAPI, Form, HTTPException, Response
from fastapi.responses import HTMLResponse

app = FastAPI(title="Hati")
expenses: list[dict[str, object]] = []


def pesos(value: Decimal) -> str:
    return f"PHP {value:,.2f}"


def balances() -> list[dict[str, str]]:
    totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    for expense in expenses:
        amount = expense["amount"]
        paid_by = expense["paid_by"]
        shares = expense["shares"]
        assert isinstance(amount, Decimal)
        assert isinstance(paid_by, str)
        assert isinstance(shares, list)
        split = (amount / len(shares)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        totals[paid_by] += amount
        for person in shares:
            totals[person] -= split

    creditors = [[person, total] for person, total in totals.items() if total > 0]
    debtors = [[person, -total] for person, total in totals.items() if total < 0]
    settlements: list[dict[str, str]] = []
    while creditors and debtors:
        creditor, credit = creditors[0]
        debtor, debt = debtors[0]
        payment = min(credit, debt).quantize(Decimal("0.01"))
        settlements.append({"from": debtor, "to": creditor, "amount": pesos(payment)})
        creditors[0][1] -= payment
        debtors[0][1] -= payment
        if creditors[0][1] == 0:
            creditors.pop(0)
        if debtors[0][1] == 0:
            debtors.pop(0)
    return settlements


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hati - shared expenses</title>
<style>
:root{color:#172554;background:#eff6ff;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#dbeafe 0,#eff6ff 270px);min-height:100vh}
main{width:min(100%,680px);margin:auto;padding:28px 20px 48px}.brand{display:flex;align-items:center;gap:10px;font-size:1.1rem;font-weight:800;letter-spacing:-.04em}
.brand-mark{display:grid;place-items:center;width:32px;height:32px;border-radius:10px;background:#2563eb;color:white;font-size:.95rem}.eyebrow{color:#1d4ed8;font-size:.75rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;margin:34px 0 8px}
h1{font-size:clamp(2rem,7vw,3rem);line-height:1.05;letter-spacing:-.06em;margin:0}.intro{color:#475569;font-size:1.05rem;line-height:1.55;margin:12px 0 24px}
.balance-card,.expense-card,.settlements-card{background:#fff;border:1px solid #dbeafe;border-radius:22px;box-shadow:0 14px 34px rgba(30,64,175,.1)}.balance-card{background:#172554;color:white;padding:22px;margin-bottom:18px}.balance-label{color:#bfdbfe;font-size:.9rem;margin:0 0 7px}.balance-card h2{font-size:1.25rem;margin:0}.balance-card p:last-child{color:#dbeafe;font-size:.92rem;margin:8px 0 0}
.expense-card,.settlements-card{padding:20px;margin-top:18px}h2{font-size:1.1rem;letter-spacing:-.02em;margin:0}.section-copy{color:#64748b;font-size:.9rem;line-height:1.45;margin:6px 0 18px}
form{display:grid;gap:14px}.field{display:grid;gap:6px}label{color:#334155;font-size:.86rem;font-weight:700}input{appearance:none;width:100%;border:1px solid #cbd5e1;border-radius:12px;background:#f8fafc;color:#172554;font:inherit;padding:13px;min-height:48px}input:focus{outline:3px solid #bfdbfe;border-color:#2563eb;background:white}
button{border:0;border-radius:12px;background:#2563eb;color:white;cursor:pointer;font:inherit;font-weight:800;min-height:50px;padding:12px 16px;transition:background .15s ease,transform .15s ease}button:hover{background:#1d4ed8}button:active{transform:translateY(1px)}
.settlement-list{display:grid;gap:10px;list-style:none;margin:0;padding:0}.settlement{display:flex;align-items:center;justify-content:space-between;gap:12px;border-radius:14px;background:#f8fafc;padding:13px}.settlement-copy{color:#475569;font-size:.92rem;line-height:1.35}.settlement strong{color:#1d4ed8;white-space:nowrap}.empty{color:#64748b;background:#f8fafc;border-radius:14px;padding:13px}
@media (max-width: 480px){main{padding:22px 16px 36px}.eyebrow{margin-top:28px}.balance-card,.expense-card,.settlements-card{border-radius:18px}.expense-card,.settlements-card{padding:17px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head><body><main>
<header><div class="brand"><span class="brand-mark" aria-hidden="true">h</span>hati</div><p class="eyebrow">Shared expenses, made simple</p>
<h1>Settle up with confidence.</h1><p class="intro">Split shared expenses with clarity, fairness, and less awkward math for everyone in the house.</p></header>
<section class="balance-card" aria-labelledby="balance-heading"><p class="balance-label">Your group</p><h2 id="balance-heading">Who owes whom</h2><p id="settlement-status">Add an expense to see the split.</p></section>
<section class="expense-card" aria-labelledby="expense-heading"><h2 id="expense-heading">Add an expense</h2><p class="section-copy">Tell Hati what you paid and who shared it.</p>
<form id="expense-form"><div class="field"><label for="description">What was it for?</label><input id="description" name="description" placeholder="e.g. Friday dinner" required></div>
<div class="field"><label for="amount">Amount in PHP</label><input id="amount" name="amount" type="number" step="0.01" min="0.01" placeholder="0.00" required></div>
<div class="field"><label for="paid_by">Who paid?</label><input id="paid_by" name="paid_by" placeholder="e.g. Ana" required></div>
<div class="field"><label for="shares">Who shares it?</label><input id="shares" name="shares" placeholder="e.g. Ana, Ben, Cara" required></div>
<button type="submit">Add expense</button></form></section>
<section class="settlements-card" aria-labelledby="settlements-heading"><h2 id="settlements-heading">Settle up</h2><p class="section-copy">Your latest balances update as you add expenses.</p>
<ul id="settlements" class="settlement-list" aria-live="polite"><li class="empty">No balances yet.</li></ul></section>
<script>
const list = document.querySelector("#settlements");
const status = document.querySelector("#settlement-status");
async function refresh() {
  const settlements = await fetch("/settlements").then(r => r.json());
  list.replaceChildren();
  if (settlements.length) {
    for (const settlement of settlements) {
      const row = document.createElement("li");
      row.className = "settlement";
      const copy = document.createElement("span");
      copy.className = "settlement-copy";
      copy.textContent = `${settlement.from} owes ${settlement.to}`;
      const amount = document.createElement("strong");
      amount.textContent = settlement.amount;
      row.append(copy, amount);
      list.append(row);
    }
  } else {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "All settled up.";
    list.append(empty);
  }
  status.textContent = settlements.length ? `${settlements.length} payment${settlements.length === 1 ? "" : "s"} to settle.` : "Everyone is settled up.";
}
document.querySelector("#expense-form").addEventListener("submit", async event => {
  event.preventDefault();
  const response = await fetch("/expenses", {method:"POST", body:new FormData(event.target)});
  if (!response.ok) return alert((await response.json()).detail);
  event.target.reset(); refresh();
});
refresh();
</script></main></body></html>"""


@app.post("/expenses")
def add_expense(
    description: str = Form(),
    amount: str = Form(),
    paid_by: str = Form(),
    shares: str = Form(),
) -> dict[str, object]:
    try:
        value = Decimal(amount)
    except InvalidOperation as exc:
        raise HTTPException(422, "Amount must be a number.") from exc
    people = [person.strip() for person in shares.split(",") if person.strip()]
    if not value.is_finite() or not description.strip() or not paid_by.strip() or not people or value <= 0:
        raise HTTPException(422, "Provide a description, positive amount, payer, and at least one roommate.")
    expenses.append({"description": description.strip(), "amount": value.quantize(Decimal("0.01")), "paid_by": paid_by.strip(), "shares": people})
    return {"ok": True, "settlements": balances()}


@app.get("/settlements")
def get_settlements() -> list[dict[str, str]]:
    return balances()


@app.post("/expenses/export")
def export_expenses() -> Response:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["description", "amount", "paid_by", "shares"])
    for expense in expenses:
        description = expense["description"]
        amount = expense["amount"]
        paid_by = expense["paid_by"]
        shares = expense["shares"]
        assert isinstance(description, str)
        assert isinstance(amount, Decimal)
        assert isinstance(paid_by, str)
        assert isinstance(shares, list)
        writer.writerow([description, f"{amount:.2f}", paid_by, ", ".join(shares)])
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="expenses.csv"'})

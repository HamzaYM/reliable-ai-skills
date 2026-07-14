type Line = { label: string; amountCents: number };

export function InvoiceSummary(props: {
  lines: Line[];
  discountCents: number;
  balanceCents: number;
}) {
  const { lines, discountCents, balanceCents } = props;
  return (
    <div className="invoice-summary">
      {lines.map((l) => (
        <div key={l.label} className="line">
          <span>{l.label}</span>
          <span>{(l.amountCents / 100).toFixed(2)}</span>
        </div>
      ))}
      {discountCents === 0 && (
        <div className="line discount">
          <span>Credit / discount</span>
          <span>{(discountCents / 100).toFixed(2)}</span>
        </div>
      )}
      {balanceCents === 0 ? (
        <div className="line total paid">
          <span>Paid in full</span>
          <span>0.00</span>
        </div>
      ) : (
        <div className="line total">
          <span>Balance due</span>
          <span>{(balanceCents / 100).toFixed(2)}</span>
        </div>
      )}
    </div>
  );
}

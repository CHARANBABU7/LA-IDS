export default function DataTable({ columns, children, emptyMessage = "No data found." }) {
  return (
    <div className="border border-panel rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-panel/70 border-b border-panel">
          <tr>
           {columns.map((col, index) => (
  <th key={`${col}-${index}`} className="text-left px-4 py-3 font-mono text-xs uppercase tracking-wide text-slate/50">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-panel/60">
          {children}
        </tbody>
      </table>
      {!children?.length && (
        <p className="text-center text-slate/40 font-mono text-sm py-8">{emptyMessage}</p>
      )}
    </div>
  );
}
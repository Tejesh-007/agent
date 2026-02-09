"use client";

interface SQLResultTableProps {
  data: string;
}

export function SQLResultTable({ data }: SQLResultTableProps) {
  return (
    <div className="bg-muted/50 rounded-lg p-3 overflow-x-auto">
      <p className="text-xs font-medium text-muted-foreground mb-1">
        Query Result
      </p>
      <pre className="text-xs whitespace-pre-wrap font-mono">{data}</pre>
    </div>
  );
}

import { useCallback } from "react";

interface FileUploadProps {
  label: string;
  file: File | null;
  onFileSelect: (file: File | null) => void;
  accept?: string;
}

export function FileUpload({
  label,
  file,
  onFileSelect,
  accept = ".csv,.xlsx,.xls",
}: FileUploadProps) {
  // handles file drop event
  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) {
        onFileSelect(droppedFile);
      }
    },
    [onFileSelect],
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  }, []);

  // handles file input change
  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0];
      if (selectedFile) {
        onFileSelect(selectedFile);
      }
    },
    [onFileSelect],
  );

  const handleRemove = useCallback(() => {
    onFileSelect(null);
  }, [onFileSelect]);

  return (
    <div className="flex-1">
      <label className="block text-sm font-medium text-slate-600 mb-2">
        {label}
      </label>

      {!file ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center 
                     hover:border-blue-400 hover:bg-blue-50 transition-colors cursor-pointer bg-white"
        >
          <input
            type="file"
            accept={accept}
            onChange={handleFileInput}
            className="hidden"
            id={`file-${label}`}
          />
          <label htmlFor={`file-${label}`} className="cursor-pointer">
            <div className="text-3xl mb-2">📄</div>
            <p className="text-slate-600 text-sm">
              Drag & drop or{" "}
              <span className="text-blue-600 hover:underline">browse</span>
            </p>
            <p className="text-slate-400 text-xs mt-1">CSV or Excel files</p>
          </label>
        </div>
      ) : (
        <div className="border border-slate-200 rounded-lg p-4 bg-white flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📋</span>
            <div>
              <p className="text-sm font-medium text-slate-700">{file.name}</p>
              <p className="text-xs text-slate-400">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>
          <button
            onClick={handleRemove}
            className="text-slate-400 hover:text-red-500 text-xl transition-colors"
            title="Remove file"
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
}

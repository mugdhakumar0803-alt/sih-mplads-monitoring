import { useState } from "react";
import { simulatePhotoVerification } from "../../utils/photoVerification";

const statusStyles = {
  verified: { bg: "bg-green-100", text: "text-green-700", label: "✅ Verified" },
  location_mismatch: { bg: "bg-red-100", text: "text-red-700", label: "🚫 Location Mismatch" },
  no_gps_data: { bg: "bg-gray-100", text: "text-gray-600", label: "⚠ No GPS Data" },
};

function PhotoUpload({ onUpload }) {
  const [stage, setStage] = useState("before");
  const [fileName, setFileName] = useState("");
  const [result, setResult] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setFileName(e.target.files[0].name);
      setResult(null);
    }
  };

  const handleUpload = () => {
    if (!fileName) return;
    setUploading(true);
    setResult(null);

    // Simulate network delay for realism
    setTimeout(() => {
      const verification = simulatePhotoVerification();
      const photo = {
        id: `PH-${Math.floor(Math.random() * 9000) + 1000}`,
        stage,
        status: verification.status,
        uploadedAt: new Date().toISOString().split("T")[0],
        distanceM: verification.distanceM,
      };
      setResult(photo);
      setUploading(false);
      if (onUpload) onUpload(photo);
    }, 900);
  };

  const handleReset = () => {
    setFileName("");
    setResult(null);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <p className="font-semibold text-navy text-sm mb-4">
        Upload Geo-Tagged Progress Photo
      </p>

      <label className="text-xs text-gray-500 block mb-1">Stage</label>
      <select
        value={stage}
        onChange={(e) => setStage(e.target.value)}
        className="border border-gray-300 rounded px-3 py-2 text-sm mb-3 w-full"
        disabled={uploading || result}
      >
        <option value="before">Before</option>
        <option value="mid">Mid-Progress</option>
        <option value="after">Completion</option>
      </select>

      <label className="text-xs text-gray-500 block mb-1">Photo</label>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={uploading || result}
        className="text-sm mb-4 w-full"
      />

      {!result && (
        <button
          onClick={handleUpload}
          disabled={!fileName || uploading}
          className="bg-navy text-white px-4 py-2 rounded text-sm font-semibold disabled:opacity-40"
        >
          {uploading ? "Verifying..." : "Upload & Verify"}
        </button>
      )}

      {result && (
        <div className="mt-2">
          <div
            className={`rounded p-3 mb-3 ${statusStyles[result.status].bg}`}
          >
            <p className={`text-sm font-semibold ${statusStyles[result.status].text}`}>
              {statusStyles[result.status].label}
            </p>
            {result.distanceM !== null && (
              <p className="text-xs text-gray-500 mt-1">
                {result.distanceM}m from registered location
              </p>
            )}
            {result.status === "no_gps_data" && (
              <p className="text-xs text-gray-500 mt-1">
                Photo metadata did not contain GPS coordinates.
              </p>
            )}
          </div>
          <button
            onClick={handleReset}
            className="text-sm text-navy underline"
          >
            Upload another photo
          </button>
        </div>
      )}
    </div>
  );
}

export default PhotoUpload;
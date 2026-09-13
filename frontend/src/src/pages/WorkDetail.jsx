import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getWorkById, getPhotosForWork, getGrievancesForWork, addPhotoToWork, statusColors } from "../utils/mockData";
import { getSLAStatus } from "../utils/slaHelper";
import PhotoUpload from "../components/PhotoVerification/PhotoUpload";

const photoStatusStyles = {
  verified: "bg-green-100 text-green-700",
  location_mismatch: "bg-red-100 text-red-700",
  duplicate_image: "bg-orange-100 text-orange-700",
  no_gps_data: "bg-gray-100 text-gray-600",
};

function WorkDetail() {
  const { workId } = useParams();
  const navigate = useNavigate();
  const work = getWorkById(workId);
  const [photos, setPhotos] = useState(getPhotosForWork(workId));
  const grievances = getGrievancesForWork(workId);
  const [showUpload, setShowUpload] = useState(false);

  if (!work) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <p className="text-gray-500">Work not found.</p>
        <button onClick={() => navigate(-1)} className="text-navy text-sm mt-2">
          ← Go back
        </button>
      </div>
    );
  }

  const handleNewPhoto = (photo) => {
    addPhotoToWork(workId, photo);
    setPhotos((prev) => [...prev, photo]);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-gray-400 mb-4"
      >
        ← Back
      </button>

      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h1 className="text-xl font-bold text-navy">{work.title}</h1>
            <p className="text-sm text-gray-400">
              {work.id} · {work.district} · {work.agency}
            </p>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColors[work.status]}`}
          >
            {work.status}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div>
            <p className="text-xs text-gray-400">Sanctioned</p>
            <p className="font-semibold text-navy">
              ₹{(work.sanctioned / 100000).toFixed(1)}L
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Spent</p>
            <p className="font-semibold text-navy">
              ₹{(work.spent / 100000).toFixed(1)}L
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Progress</p>
            <p className="font-semibold text-navy">{work.progress}%</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">Geo-Tag</p>
            <p className="font-semibold text-navy">
              {work.geoTag ? "✅ Verified" : "❌ Missing"}
            </p>
          </div>
        </div>

        {work.flags.length > 0 && (
          <div className="mt-4 flex gap-2 flex-wrap">
            {work.flags.map((flag) => (
              <span
                key={flag}
                className="bg-red-50 text-red-600 text-xs px-2 py-1 rounded"
              >
                ⚠ {flag}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Photos */}
        <div>
          <div className="bg-white border border-gray-200 rounded-lg p-5 mb-4">
            <div className="flex justify-between items-center mb-4">
              <p className="font-semibold text-navy text-sm">
                Geo-Tagged Photos ({photos.length})
              </p>
              <button
                onClick={() => setShowUpload(!showUpload)}
                className="text-xs bg-navy text-white px-3 py-1.5 rounded"
              >
                {showUpload ? "Cancel" : "+ Upload Photo"}
              </button>
            </div>

            {photos.length === 0 ? (
              <p className="text-sm text-gray-400">No photos uploaded yet.</p>
            ) : (
              <div className="space-y-3">
                {photos.map((p) => (
                  <div
                    key={p.id}
                    className="border border-gray-200 rounded p-3 flex justify-between items-center"
                  >
                    <div>
                      <p className="text-sm font-medium text-navy capitalize">
                        {p.stage} stage
                      </p>
                      <p className="text-xs text-gray-400">
                        {p.id} · {p.uploadedAt}
                        {p.distanceM !== null && ` · ${p.distanceM}m from registered location`}
                      </p>
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded font-medium ${photoStatusStyles[p.status]}`}
                    >
                      {p.status.replace("_", " ")}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {showUpload && <PhotoUpload onUpload={handleNewPhoto} />}
        </div>

        {/* Grievances */}
        <div className="bg-white border border-gray-200 rounded-lg p-5">
          <p className="font-semibold text-navy text-sm mb-4">
            Grievances on this Work ({grievances.length})
          </p>
          {grievances.length === 0 ? (
            <p className="text-sm text-gray-400">No grievances filed.</p>
          ) : (
            <div className="space-y-3">
              {grievances.map((g) => {
                const sla = getSLAStatus(g.filedAt, g.slaDeadlineDays);
                return (
                  <div key={g.id} className="border border-gray-200 rounded p-3">
                    <div className="flex justify-between items-start mb-1">
                      <p className="text-xs text-gray-400">
                        {g.id} · {g.filedBy}
                      </p>
                      <span
                        className={`text-xs font-semibold px-2 py-0.5 rounded ${
                          sla.isOverdue
                            ? "bg-red-100 text-red-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {sla.label}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{g.description}</p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default WorkDetail;
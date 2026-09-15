import { useEffect, useState } from "react";
import { getLeaderboard } from "../../api/client";

function MPLeaderboard() {
  const [level, setLevel] = useState("national");
  const [state, setState] = useState("");
  const [constituency, setConstituency] = useState("");
  const [rankings, setRankings] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadLeaderboard = async () => {
      try {
        setError("");

        const result = await getLeaderboard(level, state, constituency);

        setRankings(result.rankings || []);
      } catch (err) {
        setError(err.message);
      }
    };

    loadLeaderboard();
  }, [level, state, constituency]);

  return (
    <div>
      <div className="bg-navy text-white rounded-lg p-6 mb-6">
        <p className="text-sm text-ice">
          Citizen-driven performance measurement of completed MPLADS works.
        </p>

        <h2 className="text-2xl font-bold mt-2">
          MPLADS Citizen Performance Index
        </h2>

        <p className="text-xs text-ice mt-2">
          Scores are based on verified citizen feedback, not popularity.
        </p>
      </div>

      <div className="flex gap-2 mb-6">
        {["national", "state", "constituency"].map((item) => (
          <button
            key={item}
            onClick={() => setLevel(item)}
            className={`px-4 py-2 rounded text-sm ${
              level === item
                ? "bg-navy text-white"
                : "bg-gray-100 text-gray-600"
            }`}
          >
            {item.charAt(0).toUpperCase() + item.slice(1)}
          </button>
        ))}
      </div>

      {level === "state" && (
        <input
          value={state}
          onChange={(event) => setState(event.target.value)}
          placeholder="Enter state"
          className="border rounded px-3 py-2 mb-4 w-full"
        />
      )}

      {level === "constituency" && (
        <input
          value={constituency}
          onChange={(event) => setConstituency(event.target.value)}
          placeholder="Enter constituency"
          className="border rounded px-3 py-2 mb-4 w-full"
        />
      )}

      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

      <div className="bg-white border rounded-lg overflow-hidden">
        <div className="p-4 border-b">
          <h3 className="font-bold text-navy">
            {level.charAt(0).toUpperCase() + level.slice(1)} Leaderboard
          </h3>
        </div>

        {rankings.length === 0 ? (
          <p className="p-6 text-gray-500">
            No verified citizen ratings available yet.
          </p>
        ) : (
          <div>
            {rankings.map((mp) => (
              <div
                key={`${mp.mp_name}-${mp.constituency}`}
                className="p-5 border-b last:border-b-0"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-lg font-bold text-navy">
                      #{mp.rank} {mp.mp_name}
                    </p>

                    <p className="text-xs text-gray-500 mt-1">
                      {mp.state} · {mp.constituency}
                    </p>
                  </div>

                  <div className="text-right">
                    <p className="text-2xl font-bold text-navy">
                      {mp.citizen_performance_index}
                    </p>

                    <p className="text-xs text-gray-500">
                      Citizen Performance Index
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-5">
                  <Score label="Quality" value={mp.quality} />
                  <Score label="Usefulness" value={mp.usefulness} />
                  <Score label="Timeliness" value={mp.timeliness} />
                  <Score label="Maintenance" value={mp.maintenance} />
                  <Score label="Satisfaction" value={mp.satisfaction} />
                </div>

                <div className="mt-4 text-xs text-gray-500">
                  {mp.verified_works} verified works · {mp.citizen_responses}{" "}
                  citizen responses
                </div>

                <div className="mt-4 bg-gray-50 rounded p-4">
                  <p className="font-semibold text-sm text-navy mb-2">
                    Why this score?
                  </p>

                  <p className="text-xs text-gray-600">
                    Quality contributes 30%, usefulness 25%, timeliness 20%,
                    maintenance 15%, and citizen satisfaction 10%.
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function Score({ label, value }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>

      <p className="font-bold text-navy">{value}/5</p>
    </div>
  );
}

export default MPLeaderboard;

import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    LineChart,
    Line
} from 'recharts';

const DataDisplay = ({ data, visualizationType }) => {
    if (!data || data.length === 0) return null;

    const keys = Object.keys(data[0]);

    // If data is too large, show warning or slice
    const displayData = data.length > 50 ? data.slice(0, 50) : data;

    if (visualizationType === 'table') {
        return (
            <div className="mt-4 overflow-x-auto max-w-4xl mx-auto border border-gray-200 rounded-lg shadow-sm">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                    <thead className="bg-gray-50">
                        <tr>
                            {keys.map((key) => (
                                <th key={key} className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    {key}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {displayData.map((row, idx) => (
                            <tr key={idx} className="hover:bg-gray-50">
                                {keys.map((key) => (
                                    <td key={key} className="px-3 py-2 whitespace-nowrap text-gray-700">
                                        {String(row[key])}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
                {data.length > 50 && (
                    <div className="p-2 text-xs text-gray-500 text-center bg-gray-50">
                        Showing first 50 rows of {data.length}
                    </div>
                )}
            </div>
        );
    }

    // Visualization Logic
    if (visualizationType === 'bar' || visualizationType === 'line') {
        const XKey = keys[0]; // Assuming first column is label
        const YKey = keys[1]; // Assuming second column is value

        return (
            <div className="mt-4 h-64 w-full max-w-4xl mx-auto border border-gray-200 rounded-lg p-4 bg-white shadow-sm">
                <ResponsiveContainer width="100%" height="100%">
                    {visualizationType === 'bar' ? (
                        <BarChart data={displayData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={XKey} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey={YKey} fill="#3b82f6" />
                        </BarChart>
                    ) : (
                        <LineChart data={displayData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={XKey} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey={YKey} stroke="#8884d8" activeDot={{ r: 8 }} />
                        </LineChart>
                    )}
                </ResponsiveContainer>
            </div>
        );
    }

    return null;
};

export default DataDisplay;

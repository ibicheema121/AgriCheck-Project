import { useEffect, useState } from "react";
import { History, Loader2, AlertCircle, Download, Calendar } from "lucide-react";
import { useLanguage } from "@/contexts/LanguageContext";
import { motion } from "framer-motion";
import { sensorService, type SensorReading } from "@/services/sensorService";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function SoilHistory() {
  const { t } = useLanguage();
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(50);
  const [filteredReadings, setFilteredReadings] = useState<SensorReading[]>([]);
  const [filterDate, setFilterDate] = useState("");

  const fetchHistoricalData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await sensorService.getHistory(limit);
      setReadings(data);
      setFilteredReadings(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to fetch historical sensor data. Please ensure the backend is running."
      );
      console.error("Failed to fetch historical data:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistoricalData();
  }, [limit]);

  // Filter by date
  useEffect(() => {
    if (!filterDate) {
      setFilteredReadings(readings);
    } else {
      const filterDateObj = new Date(filterDate);
      const filtered = readings.filter((reading) => {
        const readingDate = new Date(reading.timestamp);
        return (
          readingDate.getFullYear() === filterDateObj.getFullYear() &&
          readingDate.getMonth() === filterDateObj.getMonth() &&
          readingDate.getDate() === filterDateObj.getDate()
        );
      });
      setFilteredReadings(filtered);
    }
  }, [filterDate, readings]);

  // Calculate statistics
  const stats = {
    avgNitrogen: readings.length > 0 ? (readings.reduce((sum, r) => sum + r.nitrogen, 0) / readings.length).toFixed(1) : "0",
    avgPhosphorus: readings.length > 0 ? (readings.reduce((sum, r) => sum + r.phosphorus, 0) / readings.length).toFixed(1) : "0",
    avgPotassium: readings.length > 0 ? (readings.reduce((sum, r) => sum + r.potassium, 0) / readings.length).toFixed(1) : "0",
    avgPh: readings.length > 0 ? (readings.reduce((sum, r) => sum + r.ph, 0) / readings.length).toFixed(2) : "0",
    avgTemp: readings.length > 0 ? (readings.reduce((sum, r) => sum + r.temperature, 0) / readings.length).toFixed(1) : "0",
    avgHumidity: readings.length > 0 ? (readings.reduce((sum, r) => sum + r.humidity, 0) / readings.length).toFixed(1) : "0",
    avgEC: readings.length > 0 ? (readings.reduce((sum, r) => sum + r.ec, 0) / readings.length).toFixed(2) : "0",
  };

  // Export to CSV
  const handleExportCSV = () => {
    if (filteredReadings.length === 0) {
      alert("No data to export");
      return;
    }

    const headers = [
      "Timestamp",
      "Nitrogen (mg/kg)",
      "Phosphorus (mg/kg)",
      "Potassium (mg/kg)",
      "pH Level",
      "Temperature (°C)",
      "Humidity (%)",
      "EC (µS/cm)",
    ];

    const rows = filteredReadings.map((r) => [
      new Date(r.timestamp).toLocaleString(),
      r.nitrogen,
      r.phosphorus,
      r.potassium,
      r.ph,
      r.temperature,
      r.humidity,
      r.ec,
    ]);

    const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `soil-history-${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  // Get minimum and maximum values
  const getMinMax = (key: keyof SensorReading) => {
    if (readings.length === 0) return { min: 0, max: 0 };
    const values = readings.map((r) => r[key] as number).filter((v) => typeof v === "number");
    return {
      min: Math.min(...values),
      max: Math.max(...values),
    };
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-4 sm:space-y-6 lg:space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-start sm:items-center gap-2 sm:gap-3 mb-4 sm:mb-6 px-0.5">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-primary/10 flex items-center justify-center shrink-0">
            <History className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-lg sm:text-2xl lg:text-3xl font-bold text-foreground">{t("soilHistoryHeading")}</h1>
            <p className="text-xs sm:text-sm text-muted-foreground">{t("soilHistorySubheading")}</p>
          </div>
        </div>
      </motion.div>

      {/* Loading State */}
      {isLoading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <span className="ml-2 text-muted-foreground">{t("loadingHistoricalData")}</span>
        </motion.div>
      )}

      {/* Error State */}
      {error && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </motion.div>
      )}

      {/* Content */}
      {!isLoading && !error && readings.length > 0 && (
        <>
          {/* Statistics Cards */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 sm:gap-3 lg:gap-4 px-0.5"
          >
            <Card>
              <CardHeader className="pb-2 p-2 sm:p-4">
                <CardTitle className="text-xs sm:text-sm font-semibold truncate">{t("avgN")}</CardTitle>
              </CardHeader>
              <CardContent className="p-2 sm:p-4 pt-0 sm:pt-0">
                <div className="text-xl sm:text-2xl font-bold truncate">{stats.avgNitrogen}</div>
                <p className="text-xs text-muted-foreground">{t("mgPerKg")}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2 p-2 sm:p-4">
                <CardTitle className="text-xs sm:text-sm font-semibold truncate">{t("avgPh")}</CardTitle>
              </CardHeader>
              <CardContent className="p-2 sm:p-4 pt-0 sm:pt-0">
                <div className="text-xl sm:text-2xl font-bold truncate">{stats.avgPh}</div>
                <p className="text-xs text-muted-foreground">pH</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2 p-2 sm:p-4">
                <CardTitle className="text-xs sm:text-sm font-semibold truncate">{t("avgTemp")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.avgTemp}{t("celsius")}</div>
                <p className="text-xs text-muted-foreground">{t("soilTemp")}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold">{t("avgHumidity")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.avgHumidity}{t("percent")}</div>
                <p className="text-xs text-muted-foreground">{t("humidity")}</p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Filter and Controls */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-3 items-end"
          >
            <div className="w-full sm:w-auto">
              <label className="text-sm font-semibold text-muted-foreground mb-2 block">
                {t("filterByDate")}
              </label>
              <Input
                type="date"
                value={filterDate}
                onChange={(e) => setFilterDate(e.target.value)}
                className="w-full"
              />
            </div>

            <div className="w-full sm:w-auto">
              <label className="text-sm font-semibold text-muted-foreground mb-2 block">
                {t("recordsToDisplay")}
              </label>
              <select
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="w-full px-3 py-2 rounded-md border border-input bg-background text-foreground"
              >
                <option value={20}>{t("last20Records")}</option>
                <option value={50}>{t("last50Records")}</option>
                <option value={100}>{t("last100Records")}</option>
                <option value={200}>{t("last200Records")}</option>
              </select>
            </div>

            <Button onClick={() => setFilterDate("")} variant="outline">
              {t("clearFilter")}
            </Button>

            <Button onClick={handleExportCSV} className="gap-2">
              <Download className="w-4 h-4" />
              {t("exportCsv")}
            </Button>
          </motion.div>

          {/* Data Table */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  {t("historicalReadings")} ({filteredReadings.length})
                </CardTitle>
                <CardDescription>
                  {t("displayingRecords", { count: filteredReadings.length, total: readings.length })}
                </CardDescription>
              </CardHeader>
              <CardContent className="overflow-x-auto">
                {filteredReadings.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Calendar className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>{t("noReadingsFound")}</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="text-xs">{t("timestamp")}</TableHead>
                        <TableHead className="text-xs text-right">{t("nitrogen")} ({t("mgPerKg")})</TableHead>
                        <TableHead className="text-xs text-right">{t("phosphorus")} ({t("mgPerKg")})</TableHead>
                        <TableHead className="text-xs text-right">{t("potassium")} ({t("mgPerKg")})</TableHead>
                        <TableHead className="text-xs text-right">{t("ph")}</TableHead>
                        <TableHead className="text-xs text-right">{t("soilTemp")} ({t("celsius")})</TableHead>
                        <TableHead className="text-xs text-right">{t("humidity")} ({t("percent")})</TableHead>
                        <TableHead className="text-xs text-right">{t("ec")} ({t("msPerCm")})</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredReadings.map((reading, index) => (
                        <motion.tr
                          key={reading.id}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: index * 0.02 }}
                          className="hover:bg-muted/50 transition-colors"
                        >
                          <TableCell className="text-xs whitespace-nowrap font-mono">
                            {formatDate(reading.timestamp)}
                          </TableCell>
                          <TableCell className="text-xs text-right">{reading.nitrogen}</TableCell>
                          <TableCell className="text-xs text-right">{reading.phosphorus}</TableCell>
                          <TableCell className="text-xs text-right">{reading.potassium}</TableCell>
                          <TableCell className="text-xs text-right font-semibold">
                            <span
                              className={`px-2 py-1 rounded ${
                                reading.ph >= 6.0 && reading.ph <= 7.0
                                  ? "bg-green-100 text-green-700"
                                  : "bg-orange-100 text-orange-700"
                              }`}
                            >
                              {reading.ph}
                            </span>
                          </TableCell>
                          <TableCell className="text-xs text-right">{reading.temperature}°C</TableCell>
                          <TableCell className="text-xs text-right">{reading.humidity}%</TableCell>
                          <TableCell className="text-xs text-right">{reading.ec}</TableCell>
                        </motion.tr>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Min/Max Summary */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
          >
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold">{t("nitrogenRange")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xs space-y-1">
                  <div>
                    {t("min")}: <span className="font-mono font-bold">{getMinMax("nitrogen").min}</span>
                  </div>
                  <div>
                    {t("max")}: <span className="font-mono font-bold">{getMinMax("nitrogen").max}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold">{t("phRange")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xs space-y-1">
                  <div>
                    {t("min")}: <span className="font-mono font-bold">{getMinMax("ph").min.toFixed(2)}</span>
                  </div>
                  <div>
                    {t("max")}: <span className="font-mono font-bold">{getMinMax("ph").max.toFixed(2)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold">{t("temperatureRange")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xs space-y-1">
                  <div>
                    {t("min")}:{" "}
                    <span className="font-mono font-bold">{getMinMax("temperature").min.toFixed(1)}{t("celsius")}</span>
                  </div>
                  <div>
                    {t("max")}:{" "}
                    <span className="font-mono font-bold">{getMinMax("temperature").max.toFixed(1)}{t("celsius")}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold">{t("ecRange")}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xs space-y-1">
                  <div>
                    {t("min")}:{" "}
                    <span className="font-mono font-bold">{getMinMax("ec").min.toFixed(2)}
                    </span>
                  </div>
                  <div>
                    {t("max")}:{" "}
                    <span className="font-mono font-bold">{getMinMax("ec").max.toFixed(2)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </>
      )}

      {/* Empty State */}
      {!isLoading && !error && readings.length === 0 && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="text-center py-12">
            <History className="w-12 h-12 mx-auto mb-4 opacity-30" />
            <p className="text-muted-foreground mb-4">{t("noDataAvailable")}</p>
            <p className="text-sm text-muted-foreground">{t("uploadFirst")}</p>
          </Card>
        </motion.div>
      )}
    </div>
  );
}

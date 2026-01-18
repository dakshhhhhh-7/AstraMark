import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle2, XCircle, TrendingUp, AlertTriangle } from "lucide-react";

export function SWOTAnalysisGrid({ marketAnalysis }) {
    // Fallback if strengths/weaknesses are missing (backwards compatibility)
    const strengths = marketAnalysis.strengths || ["High Growth Potential", "First Mover Advantage"];
    const weaknesses = marketAnalysis.weaknesses || ["Limited Brand Awareness", "Resource Constraints"];
    const opportunities = marketAnalysis.opportunities || [];
    const risks = marketAnalysis.risks || [];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Strengths */}
            <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-3">
                        <CheckCircle2 className="w-5 h-5 text-green-400" />
                        <h3 className="text-white font-semibold">Strengths</h3>
                    </div>
                    <ul className="space-y-2">
                        {strengths.map((item, idx) => (
                            <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-500/50 mt-1.5 flex-shrink-0" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </CardContent>
            </Card>

            {/* Weaknesses */}
            <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-3">
                        <XCircle className="w-5 h-5 text-red-400" />
                        <h3 className="text-white font-semibold">Weaknesses</h3>
                    </div>
                    <ul className="space-y-2">
                        {weaknesses.map((item, idx) => (
                            <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-red-500/50 mt-1.5 flex-shrink-0" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </CardContent>
            </Card>

            {/* Opportunities */}
            <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-3">
                        <TrendingUp className="w-5 h-5 text-blue-400" />
                        <h3 className="text-white font-semibold">Opportunities</h3>
                    </div>
                    <ul className="space-y-2">
                        {opportunities.map((item, idx) => (
                            <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-blue-500/50 mt-1.5 flex-shrink-0" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </CardContent>
            </Card>

            {/* Threats */}
            <Card className="bg-slate-900/50 border-slate-800">
                <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-3">
                        <AlertTriangle className="w-5 h-5 text-yellow-400" />
                        <h3 className="text-white font-semibold">Threats</h3>
                    </div>
                    <ul className="space-y-2">
                        {risks.map((item, idx) => (
                            <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-yellow-500/50 mt-1.5 flex-shrink-0" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </CardContent>
            </Card>
        </div>
    );
}

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Check, Sparkles } from "lucide-react";

const plans = [
    {
        id: "starter",
        name: "Starter",
        price: 19,
        period: "month",
        features: [
            "Basic marketing strategies",
            "Limited reports",
            "5 analyses/month"
        ],
        color: "from-green-400 to-emerald-500",
        buttonColor: "bg-green-600 hover:bg-green-700",
        popular: false
    },
    {
        id: "pro",
        name: "Pro",
        price: 49,
        period: "month",
        features: [
            "Full marketing + data analysis",
            "Business plans",
            "Competitor research",
            "30 analyses/month"
        ],
        color: "from-blue-400 to-indigo-500",
        buttonColor: "bg-blue-600 hover:bg-blue-700",
        popular: true
    },
    {
        id: "growth",
        name: "Growth",
        price: 99,
        period: "month",
        features: [
            "Advanced analytics",
            "Revenue forecasting",
            "Automation planning",
            "Export reports (PDF/Excel)",
            "100 analyses/month"
        ],
        color: "from-purple-400 to-pink-500",
        buttonColor: "bg-purple-600 hover:bg-purple-700",
        popular: false
    },
    {
        id: "enterprise",
        name: "Enterprise",
        price: "Custom",
        period: "",
        features: [
            "API access",
            "Team accounts",
            "Custom AI tuning",
            "White-label reports"
        ],
        color: "from-slate-400 to-slate-500",
        buttonColor: "bg-slate-600 hover:bg-slate-700",
        popular: false
    }
];

export function PricingModal({ isOpen, onClose }) {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="max-w-4xl bg-slate-950 border-slate-800 text-white">
                <DialogHeader>
                    <DialogTitle className="text-3xl font-bold text-center mb-2">
                        Choose Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">Growth Plan</span>
                    </DialogTitle>
                    <DialogDescription className="text-center text-slate-400 text-lg">
                        Unlock the full power of AI marketing intelligence
                    </DialogDescription>
                </DialogHeader>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
                    {plans.map((plan) => (
                        <div
                            key={plan.id}
                            className={`relative rounded-xl border ${plan.popular ? 'border-purple-500 bg-slate-900/80' : 'border-slate-800 bg-slate-900/40'} p-6 flex flex-col`}
                        >
                            {plan.popular && (
                                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1">
                                    <Sparkles className="w-3 h-3" /> BEST VALUE
                                </div>
                            )}

                            <div className="mb-4">
                                <h3 className={`text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r ${plan.color}`}>
                                    {plan.name}
                                </h3>
                                <div className="flex items-baseline gap-1 mt-2">
                                    <span className="text-3xl font-bold text-white">
                                        {typeof plan.price === 'number' ? `$${plan.price}` : plan.price}
                                    </span>
                                    {plan.period && <span className="text-slate-400">/{plan.period}</span>}
                                </div>
                            </div>

                            <ul className="space-y-3 mb-6 flex-1">
                                {plan.features.map((feature, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                                        <Check className={`w-4 h-4 mt-0.5 shrink-0 text-white`} />
                                        {feature}
                                    </li>
                                ))}
                            </ul>

                            <Button className={`w-full ${plan.buttonColor} text-white font-semibold`}>
                                {plan.id === 'enterprise' ? 'Contact Sales' : 'Get Started'}
                            </Button>
                        </div>
                    ))}
                </div>
            </DialogContent>
        </Dialog>
    );
}

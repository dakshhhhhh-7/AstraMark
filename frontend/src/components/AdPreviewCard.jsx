import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { MessageCircle, Heart, Share2, MoreHorizontal, ExternalLink } from "lucide-react";

export function AdPreviewCard({ platform, content, headline }) {
    const isMeta = platform?.toLowerCase().includes('social') || platform?.toLowerCase().includes('meta') || platform?.toLowerCase().includes('instagram');
    const isGoogle = platform?.toLowerCase().includes('seo') || platform?.toLowerCase().includes('ads') || platform?.toLowerCase().includes('google');

    if (isMeta) {
        return (
            <Card className="max-w-sm mx-auto bg-white dark:bg-black border border-slate-200 dark:border-slate-800 overflow-hidden">
                {/* Instagram/FB Style Header */}
                <div className="p-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Avatar className="w-8 h-8">
                            <AvatarImage src="/placeholder-logo.png" />
                            <AvatarFallback className="bg-gradient-to-br from-purple-500 to-pink-500 text-white text-xs">AM</AvatarFallback>
                        </Avatar>
                        <div>
                            <div className="text-sm font-semibold text-slate-900 dark:text-white">AstraMark Brand</div>
                            <div className="text-xs text-slate-500">Sponsored</div>
                        </div>
                    </div>
                    <MoreHorizontal className="w-5 h-5 text-slate-500" />
                </div>

                {/* Ad Image Mockup */}
                <div className="aspect-square bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400">
                    <span className="text-xs">Dynamic Ad Visual Generator (Preview)</span>
                </div>

                {/* Action Bar */}
                <div className="p-3">
                    <div className="bg-blue-600 text-white text-center py-2 rounded font-semibold text-sm mb-3">
                        Learn More
                    </div>
                    <div className="flex items-center gap-4 mb-3">
                        <Heart className="w-6 h-6 text-slate-900 dark:text-white" />
                        <MessageCircle className="w-6 h-6 text-slate-900 dark:text-white" />
                        <Share2 className="w-6 h-6 text-slate-900 dark:text-white" />
                    </div>
                    <div className="text-sm">
                        <span className="font-semibold text-slate-900 dark:text-white">AstraMark Brand</span>
                        <span className="text-slate-800 dark:text-slate-200 ml-2">
                            {content || "Experience the future of marketing with our AI-driven solutions. Scale faster today! #Growth #AI"}
                        </span>
                    </div>
                </div>
            </Card>
        );
    }

    // Google Search Style Preview
    return (
        <Card className="bg-white p-4 border border-slate-200 shadow-sm max-w-md">
            <div className="flex items-center gap-1 mb-1">
                <span className="font-bold text-black text-sm">Ad</span>
                <span className="text-xs text-slate-600">• www.astramark.ai/growth</span>
            </div>
            <div className="text-blue-700 text-xl hover:underline cursor-pointer mb-1">
                {headline || "AstraMark - AI Marketing Intelligence"}
            </div>
            <div className="text-slate-600 text-sm">
                {content || "Unlock premium market insights and competitor data. Generate comprehensive strategies in seconds. Start your growth journey now."}
            </div>
            <div className="mt-2 flex gap-2">
                <span className="text-xs text-blue-700 hover:underline">Pricing</span>
                <span className="text-xs text-blue-700 hover:underline">Features</span>
                <span className="text-xs text-blue-700 hover:underline">Case Studies</span>
            </div>
        </Card>
    );
}

import { NextResponse } from "next/server";

const BACKEND_TRADES_URL = `http://backend:5001/get_trades`;

export async function GET() {
    try {
        const response = await fetch(BACKEND_TRADES_URL, {
            cache: 'no-store',
        });

        if (!response.ok) {
            console.error(`Backend responded with status ${response.status}`);
            return NextResponse.json(
                { error: `Backend error: ${response.status}`, trades: [], count: 0 },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error) {
        console.error("Error fetching trades from backend:", error);

        return NextResponse.json(
            { 
                error: "Failed to fetch trades", 
                details: error.message,
                trades: [],
                count: 0
            },
            { status: 500 }
        );
    }
}

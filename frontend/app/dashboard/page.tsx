import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import PillarRadar from "@/components/pillar-radar"

export default function Dashboard() {
  return (
    <div className="p-10 space-y-8">

      <div className="grid grid-cols-3 gap-6">

        <Card>
          <CardHeader>
            <CardTitle>Global Score</CardTitle>
          </CardHeader>
          <CardContent>82</CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>XP</CardTitle>
          </CardHeader>
          <CardContent>1250</CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Habits Completed</CardTitle>
          </CardHeader>
          <CardContent>5</CardContent>
        </Card>

      </div>

      <Card>
        <CardHeader>
          <CardTitle>Life Balance</CardTitle>
        </CardHeader>
        <CardContent>
          <PillarRadar />
        </CardContent>
      </Card>

    </div>
  )
}
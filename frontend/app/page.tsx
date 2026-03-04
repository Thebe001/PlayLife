import Link from "next/link"

export default function Home() {

  return (

    <div style={{padding:"40px"}}>

      <h1>PlayUrLife</h1>

      <Link href="/dashboard">Open Dashboard</Link>

    </div>

  )

}
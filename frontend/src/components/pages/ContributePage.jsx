import { useNavigate } from "react-router-dom"
import { useContext } from "react"
import { MapContext } from "../../App"
import { IoIosArrowBack } from "react-icons/io"
import { SiMapbox, SiOpenstreetmap } from "react-icons/si"

const ContributePage = () => {

    const navigate = useNavigate()
    const value = useContext(MapContext)

    return (
        <div className='w-full bg-white opacity-90 pb-[64px] md:pb-0'>
            <div 
            className='h-14 flex items-center cursor-pointer border-b-2 border-gray2 md:hidden'
            onClick={() => navigate('/settings')}
            >
                <div className='h-14 w-14 flex justify-center items-center'>
                    <IoIosArrowBack
                    className='h-8 w-8 text-gray4'
                    />
                </div>
                <h1 className='text-gray4 text-lg'>Back to Settings</h1>
            </div>
            <div className='w-full h-full scrollable overflow-auto'>
                <div className='px-6 py-4 border-b-2 border-gray2'>
                    <h1 className='text-5xl font-bold'>Contribute</h1>
                </div>
                <div className="px-6 py-4">
                    <h1 className='font-semibold'>Help us improve your bus experience! Your input is invaluable in making our bus tracking app even better. By contributing to OpenStreetMap and Mapbox, reporting issues, and sharing your feedback, you're helping to create a more accurate and reliable service for everyone.</h1>
                </div>
                <a 
                className='flex justify-center items-center p-3'
                href='https://apps.mapbox.com/feedback/'
                >
                    <div className='flex items-center h-10 w-fit rounded-xl bg-blue3 cursor-pointer hover:bg-blue4 transition duration-200'>
                        <div className='h-10 w-10 flex justify-center items-center'>
                            <SiMapbox className='w-6 h-6 text-white'/>
                        </div>
                        <h1 className='text-white pr-3'>Contribute to Mapbox</h1>
                    </div>
                </a>
                <div className='flex justify-center items-center p-3'>
                    <a
                    className='flex items-center h-10 w-fit rounded-xl bg-blue3 cursor-pointer hover:bg-blue4 transition duration-200'
                    href='https://wiki.openstreetmap.org/wiki/How_to_contribute'
                    >
                        <div className='h-10 w-10 flex justify-center items-center'>
                            <SiOpenstreetmap className='w-6 h-6 text-white'/>
                        </div>
                        <h1 className='text-white pr-3'>Contribute to OpenStreetMaps</h1>
                    </a>
                </div>
                <div className='flex justify-center items-center p-3'>
                    <div 
                    className='flex items-center h-10 w-fit rounded-xl bg-blue3 cursor-pointer hover:bg-blue4 transition duration-200'
                    onClick={() => navigate('/feedback')}
                    >
                        <h1 className='text-white px-3'>Give us feedback</h1>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ContributePage
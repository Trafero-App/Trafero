import { useNavigate } from "react-router-dom"
import { useContext } from "react"
import { MapContext } from "../../App"
import { IoIosArrowBack } from "react-icons/io"

const AboutUsPage = () => {

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
                <div className='px-6 min-h-20 py-3.5 flex items-center border-b-2 border-gray2 w-full h-fit'>
                    <h1 className='text-5xl font-bold'>About Us</h1>
                </div>
                <h1 className='px-6 pt-5 pb-3 font-bold text-xl'>Welcome to [App Name]</h1>
                <h1 className='font-semibold px-6'>At [App Name], we believe that navigating public transportation should be
                seamless, efficient, and stress-free. Our mission is to address the
                longstanding challenges faced by commuters and bus drivers in Lebanon by
                providing a cutting-edge solution that enhances the public transportation
                experience for everyone.</h1>
                <h1 className='px-6 pt-5 pb-3 font-bold text-xl'>Our Story</h1>
                <h1 className='font-semibold px-6'>Public transportation in Lebanon has long been plagued by issues such as
                outdated routes, unreliable schedules, and a lack of real-time information. As
                a team of passionate developers and problem-solvers, we recognized these
                challenges and set out to create an innovative application that would revolutionize
                public transportation in Lebanon.</h1>
                <h1 className='px-6 pt-5 pb-3 font-bold text-xl'>Our Vision</h1>
                <h1 className='font-semibold px-6'>We envision a future where public transportation in Lebanon is efficient,
                accessible, and user-friendly. Our goal is to continuously improve our
                application by expanding coverage, enhancing data accuracy, and incorporating
                advanced technology. </h1>
                <h1 className='px-6 pt-5 pb-3 font-bold text-xl'>Join us on Our Journey</h1>
                <h1 className='font-semibold px-6'>We invite you to explore our application and experience the difference
                for yourself. Your feedback and support are invaluable as we work towards a
                better public transportation system for Lebanon. Together, we can make
                commuting a more pleasant and reliable experience for everyone.</h1>
                <div className="min-h-10 flex justify-center items-center mt-5 border-t-2 border-gray1">
                    <h1 className='px-6 py-5 font-bold'>A project by Marc Abou Serhal, Jawad Marji, Hussein Termos & Ali Zahreddine</h1>
                </div>
            </div>
        </div>
    )
}

export default AboutUsPage
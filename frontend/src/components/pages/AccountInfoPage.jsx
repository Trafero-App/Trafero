import { useContext } from "react"
import { MapContext } from "../../App"
import { useNavigate } from "react-router-dom";
import {IoIosArrowBack} from 'react-icons/io'
import NeedToLoginPrompt from "../NeedToLoginPrompt";

function formatDate(dateString) {
    const dateParts = dateString.split('-');
    const year = dateParts[0];
    const month = dateParts[1];
    const day = dateParts[2];   
  
  
    // Create a Date object to access formatting options
    const dateObj = new Date(year, month - 1, day); // Month is 0-indexed
  
    // Get day, month name, and year components
    const dayOfMonth = dateObj.getDate();
    const monthName = dateObj.toLocaleString('en-US', { month: 'long' });
    const yearName = dateObj.getFullYear();
  
    // Construct the formatted string
    return `${dayOfMonth} ${monthName} ${yearName}`;
  }

const AccountInfoPage = () => {

    const navigate = useNavigate()
    const value = useContext(MapContext)
    const {isLoggedIn, firstName, lastName, userType, email, phoneNumber, dateOfBirth, vehicleBrand, vehicleType, vehicleModel, vehicleColor, licensePlate} = value

    return (
        isLoggedIn ?
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
            <div className='w-full h-full scrollable'>
                <div className='px-6 py-4 border-b-2 border-gray2'>
                    <h1 className='text-5xl font-bold'>Account Information</h1>
                </div>
                <div className='px-6 py-4 border-b-2 border-gray2'>
                    <h1 className='text-lg font-bold pb-1'>Personal Information</h1>
                    <h1 className='text-md pb-1'><span className='font-semibold'>Full Name: </span>{` ${firstName} ${lastName}`}</h1>
                    <h1 className='text-md pb-1'><span className='font-semibold'>Account Type: </span>{` ${userType=='passenger' ? 'Passenger' : 'Driver'}`}</h1>
                    <h1 className='text-md'><span className='font-semibold'>Date of Birth: </span>{` ${formatDate(dateOfBirth)}`}</h1>
                </div>
                {userType=='driver' &&
                <div className='px-6 py-4 border-b-2 border-gray2'>
                    <h1 className='text-lg font-bold pb-1'>Vehicle Information</h1>
                    <h1 className='text-md pb-1'><span className='font-semibold'>Type: </span>{` ${vehicleType=='van' ? 'Van' : 'Bus'}`}</h1>
                    <h1 className='text-md pb-1'><span className='font-semibold'>Brand: </span>{` ${vehicleBrand}`}</h1>
                    <h1 className='text-md pb-1'><span className='font-semibold'>Model: </span>{` ${vehicleModel}`}</h1>
                    <h1 className='text-md pb-1'><span className='font-semibold'>Color: </span>{` ${vehicleColor}`}</h1>
                    <h1 className='text-md'><span className='font-semibold'>License Plate: </span>{` ${licensePlate}`}</h1>
                </div>
                }
                <div className='px-6 py-4 border-b-2 border-gray2'>
                    <h1 className='text-lg font-bold pb-1'>Credentials</h1>
                    <h1 className='text-md pb-1'><span className='font-semibold'>Email: </span>{` ${email ? email : 'None linked to this account'}`}</h1>
                    <h1 className='text-md'><span className='font-semibold'>Phone Number: </span>{` ${phoneNumber ? phoneNumber : 'None linked to this account'}`}</h1>
                </div>
            </div>
        </div>
        :
        <NeedToLoginPrompt message='You must be logged in to access this page' setNeedsToLogin={(param) => {}}/>
    )
}

export default AccountInfoPage
import {NavLink} from 'react-router-dom'

const NavigationMenuButton = ({
        to, 
        Icon,
        text
    }) => {
    return (
        <NavLink 
            to={to}
        >
            {({isActive}) => 
            <div className={`${isActive && 'text-blue4 font-semibold'} h-full mx-1 w-16 flex flex-col justify-center items-center`}>
                <div className='rounded-[3.5rem] w-14 h-7 md:rounded-[3rem] md:w-12 md:h-6 flex justify-center items-center mb-1 transition duration-200'>
                    <Icon className={`${isActive && 'text-blue4'} w-5 h-5 text-black transition duration-200`}/>
                </div>
                <h1 className='text-sm md:text-xs transition duration-200'>{text}</h1>
            </div>
            }
        </NavLink>
    )
}

export default NavigationMenuButton
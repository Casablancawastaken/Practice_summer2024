import React, { useState } from 'react';
import { Center, FormControl, FormLabel, Input, Flex, Button, Spinner, Box } from '@chakra-ui/react';
import { Link } from "react-router-dom";
import VacancyCard from '../components/VacancyCard';

function SearchByCompanyPage() {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [vacancies, setVacancies] = useState([]);
    const [error, setError] = useState(null);
    const handleInputChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSearch = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`http://127.0.0.1:8000/search_by_company?company_name=${query}`);
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            const data = await response.json();
            setVacancies(data);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };
    return (
        <Center mt={"30px"}>
            <Flex flexDir={"column"} gap={'20px'}>
                <Flex gap={"50px"} justify={"space-between"}>
                    <Link to={"/"}>
                        <Button colorScheme='teal' variant='solid'>
                            Поиск по названию
                        </Button>
                    </Link>
                    <Link to={"/searchByCompany"}>
                        <Button colorScheme='teal' variant='solid'>
                            Поиск в базе по компании
                        </Button>
                    </Link>
                    <Link to={"/searchByVacancy"}>
                        <Button colorScheme='teal' variant='solid'>
                            Поиск в базе по вакансии
                        </Button>
                    </Link>
                </Flex>
                <FormControl>
                    <FormLabel>Поиск в базе по вакансии</FormLabel>
                    <Input placeholder='Введите запрос' value={query} onChange={handleInputChange} />
                </FormControl>
                <Button colorScheme='teal' variant='solid' onClick={handleSearch}>
                    Отправить запрос
                </Button>

                {loading && <Center><Spinner size="xl" mt="4" /></Center>}
                {error && <Box color="red.500" mt="4">{"Вакансии отсутствуют"}</Box>}

                {vacancies.length > 0 && (
                    <Flex flexDir="column" mt="4">
                        {vacancies.map((vacancy, index) => (
                            <VacancyCard key={index} {...vacancy} />
                        ))}
                    </Flex>
                )}
            </Flex>
        </Center>
    );
}

export default SearchByCompanyPage;